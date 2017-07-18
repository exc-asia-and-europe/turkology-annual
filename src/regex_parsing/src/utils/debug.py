'''

'''

import sys

class Logger(object):
    """
    Provide easy methods for bug tracking.
    """
    
    @staticmethod
    def log(class_, method, msg):
        """
        Print out a message from given method and class.

        @type class_: classobj
        @param class_: a given class
        @type method: instancemethod
        @param method: a given method of class C{class_}
        @type msg: str
        @param msg: a given message
        @rtype: NoneType
        @return: None
        """
        sys.stderr.write(('\n' +
                          '========================================\n' +
                          ' - debug message\n' +
                          ' -----------------\n' +
                          '   + class:   %s\n' +
                          '   + method:  %s\n' +
                          '   + message: %s\n' +
                          '========================================\n\n')%(str(class_),
                                                                           str(method),
                                                                           str(msg)))