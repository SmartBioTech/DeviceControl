import subprocess

HEADER = \
    '''#!/usr/bin/env gosh

    (use util.match)
    (use sad.channel3-rv)
    (use sad.gauche)
    (use srfi-19)
    (use sad.rendezvous)
    (use sad.binary-channels)
    (use util.list)
    (use gauche.threads)
    (use sad.regression)

    '''

DEFINITION_1 = '''
(define '''

DEFINITION_2 = '''
  (make-rpc
   (make-binary-unix-client
     "/tmp/devbus" "'''

DEFINITION_3 = '''")))

(spawn-rendezvous-selector-loop)

'''


class SchemeManager:
    def __init__(self, ID, address, folder='/root/control/'):
        self.ID = ID
        self.address = address
        self.folder = folder

        self.definition = DEFINITION_1 + self.ID + DEFINITION_2 + str(self.address) + DEFINITION_3
        self.command = ["(print (rpc2 " + self.ID + " `(", ")))"]
        self.filename = self.folder + 'script_' + self.ID + '.scm'

    def write_scm_file(self, commands):
        """
        Creates a Scheme script by composing HEADER and DEFINITION constants with given arguments
        """
        with open(self.filename, 'w') as file:
            file.write(HEADER)
            file.write(self.definition)
            for command in commands:
                file.write(self.command[0] + command.request + " " + " ".join(map(str, command.args)) + self.command[1])

    def execute(self, commands):
        """
        Reads output from bioreactor by calling a Scheme script
        """
        self.write_scm_file(commands)

        pipes = subprocess.Popen(['gosh', self.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = pipes.communicate()

        if stderr:
            raise Exception(stderr.decode("utf-8"))

        return stdout.decode("utf-8").split("\n")[:-1]

    @staticmethod
    def to_scheme_bool(value):
        return "#t" if value else "#f"
