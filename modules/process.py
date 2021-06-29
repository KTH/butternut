"""process.py

Util functions for working with command line calls"""

__author__ = 'tinglev@kth.se'

import subprocess
import os
import logging

def run_with_output(cmd):
    try:
        logger = logging.getLogger(__name__)
        logger.debug('Running command with output: "%s"', cmd)
        completed_process = subprocess.run(f'{cmd}', shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           close_fds=True)
        # Reap eventually orphaned child processes left by command that got adopted by us
        # as we are PID 1 when running in Docker container
        try:
            while True:
                os.waitpid(-1, 0)
        except:
            pass
                                           
        if completed_process.stderr:
            return completed_process.stderr
        return completed_process.stdout
    except subprocess.CalledProcessError as cpe:
        logger.error('Shell command gave error with output "%s"', str(cpe.output).rstrip('\n'))
        raise
