import datetime
import logging
import subprocess
import sys
import time
from typing import Dict, List, Union, Tuple

from ..log_pipe import LogPipe


class ExecutionTimeOut(Exception):
    """Raised when the input value is too large"""
    pass


class Task:
    """
    Task class
    """

    __avail_container_tech = ['docker', 'shifter', 'singularity']

    def __init__(self, commands: Union[str, List[str]],
                 n_threads: int = 1,
                 container_tech: str = None,
                 container_image: str = None,
                 container_args: str = None):
        f"""
        Task object constructor
        :param commands: Commands to execute. Accepted formats: [str, List[str]].
        :param n_threads: Number of threads for the task.
        :param container_tech: Options are: {self.__avail_container_tech}.
        :param container_image: Name of the image to use.
        :param container_args: Extra arguments that may be needed.
        """

        self.__logger = logging.getLogger('task')

        if isinstance(commands, list):
            self.__commands = commands
        elif isinstance(commands, str):
            self.__commands = [commands]
        else:
            raise Exception(f'Unknown task commands type: {type(commands)}')

        self.__n_threads = n_threads

        # Containerization technology
        if container_tech is not None and container_tech not in self.__avail_container_tech:
            raise Exception(f'Unsupported containerization technology: "{container_tech}". '
                            f'Available options are: {self.__avail_container_tech}')

        if container_tech is not None and container_image is None:
            raise Exception(f'Containerization technology specified ("{container_tech}") without an image.')

        self.__container_tech = container_tech
        self.__container_image = container_image
        self.__container_args = '' if container_args is None else container_args

    def __str__(self) -> str:
        """
        Representation method for print statement
        :return:
        """
        return f'Task<cmds:{self.__commands},' \
               f'n_threads:{self.__n_threads}, ' \
               f'container_tech:{self.__container_tech}, ' \
               f'container_image:{self.__container_image}, ' \
               f'container_args:{self.__container_args}>'

    @property
    def n_threads(self) -> int:
        """
        Get the number of thread requested for this task
        :return:
        """
        return self.__n_threads

    @property
    def commands(self) -> List[str]:
        """
        Get the list of commands
        :return:
        """
        return self.__commands

    @property
    def container_tech(self) -> str:
        """
        Get the job container technology
        :return:
        """
        return self.__container_tech

    @property
    def container_image(self) -> str:
        """
        Get the container image
        :return:
        """
        return self.__container_image

    @property
    def container_args(self) -> str:
        """
        Get the container extra arguments
        :return:
        """
        return self.__container_args

    def as_dict(self) -> dict:
        """
        Return the task as a dictionary
        :return:
        """
        dictionary = {}
        for key, value in vars(self).items():
            key = key.replace(f'_{self.__class__.__name__}__', '')
            if key.find('logger') != -1:
                continue
            dictionary[key] = value
        return dictionary

    @staticmethod
    def json_encoder(obj: 'Task') -> Dict:
        """
        JSon encoder for the task
        :param obj:
        :return:
        """
        return obj.as_dict()

    @staticmethod
    def __get_command(task: 'Task') -> str:
        """
        Format the command and return a single line command. It takes care of adding the containerization.
        :param task: input Task object
        :return:
        """
        formatted_command = ' && '.join(task.commands)

        if task.container_tech is None:
            pass
        elif task.container_tech == 'shifter':
            formatted_command = f'shifter --image={task.container_image} {task.container_args} /bin/bash -c \'{formatted_command}\''
        else:
            raise Exception(f'Containerization technology {task.container_tech} not supported yet.')

        return formatted_command

    def command(self) -> str:
        """
        Get the command as a single string
        :return:
        """
        return Task.__get_command(self)

    def execute(self, timeout_hour=-1) -> Tuple[int, str, str]:
        """
        Execute the task
        :return:
        """
        formatted_command = Task.__get_command(self)

        self.__logger.info(f'Starting execution of the command: {formatted_command}')

        args = {}
        if timeout_hour > 0:
            args['timeout'] = timeout_hour * 3600

        self.__logger.info(f'Execution starts at: {datetime.datetime.now()}')
        execution_start = time.time()

        try:
            sys.stdout = LogPipe(self.__logger, logging.INFO)
            sys.stderr = LogPipe(self.__logger, logging.ERROR)
            results = subprocess.run(formatted_command, shell=True, text=True, stdout=sys.stdout, stderr=sys.stderr)

        finally:
            sys.stdout.close()
            sys.stderr.close()

            stdout = sys.stdout.text()
            stderr = sys.stderr.text()

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        execution_time = datetime.timedelta(seconds=time.time() - execution_start)
        self.__logger.info(f'Execution ends at: {datetime.datetime.now()} with the exit code: {results.returncode}')
        self.__logger.info(f'Execution time: {execution_time} ({execution_time.total_seconds()} s)')

        return results.returncode, stdout, stderr

    @classmethod
    def from_dict(cls, dictionary: Dict) -> 'Task':
        """
        Create a task from a dictionary
        :param dictionary: input dictionary
        :return:
        """
        return cls(**dictionary)

    @classmethod
    def task_array(cls, task_commands: List[List[str]], **kwargs) -> List['Task']:
        """
        Create a task array from an array of commands. All the tasks will
        :param task_commands: input array of commands. Expected format: [[cmd1, cmd2, ..., cmdN], ... , [cmd1, cmd2, ..., cmdN]]
        :param kwargs:
        :return: A list of Task object
        """
        return [cls(commands=commands, **kwargs) for commands in task_commands]
