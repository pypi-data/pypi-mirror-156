import io
import logging
import threading
import os


class LogPipe(threading.Thread):

    def __init__(self, logger, level):
        """Setup the object with a logger and a loglevel
        and start the thread
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.logger = logger
        self.level = level
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.__io = io.StringIO()

        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe"""
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything."""
        for line in iter(self.pipeReader.readline, ''):
            self.logger.log(self.level, line.strip('\n'))
            self.__io.write(line)

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe."""
        os.close(self.fdWrite)

    def flush(self):
        """If you code has something like this sys.stdout.flush"""
        pass

    def io(self):
        return self.__io


    def text(self):
        return self.__io.getvalue()
