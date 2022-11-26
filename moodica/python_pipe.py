import win32file
import win32pipe
import pywintypes


class PipeClient:
    fileHandle = 0

    def __init__(self, name):
        self.fileHandle = win32file.CreateFile(
            "\\\\.\\pipe\\" + name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None)

    def read_message(self):
        """
        Using the current Pipe Server and read from there
        :return the Pipe left and Message:
        """
        left, data = win32file.ReadFile(self.fileHandle, 4096)
        data = data.decode()
        data = data[1:]
        return left, data

    def close_pipe(self):
        win32file.CloseHandle(self.fileHandle)


""" if __name__ == '__main__':
    DemoT = PipeClient("Demo")
    print(DemoT.read_message()) """


class PipeServer:
    fileHandle = 0

    def __init__(self, name):
        self.fileHandle = win32pipe.CreateNamedPipe(
            "\\\\.\\pipe\\" + name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65536, 65536,
            0,
            None)
        #print("waiting for client")
        win32pipe.ConnectNamedPipe(self.fileHandle, None)
        #print("got client")

    def send_message(self, msg):
        try:
            #print(f"writing message {msg}")
            # convert to bytes
            msg = str.encode(msg)
            win32file.WriteFile(self.fileHandle, msg)
            #print("finished now")

        except:
            print(f"Error == py Server")

    def close_pipe(self):
        win32file.CloseHandle(self.fileHandle)
