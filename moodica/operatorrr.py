import model_prediction
import python_pipe
import time


def activate_server(img_path):
    """
    This function activates the server (model prediction and
    Spotify recommendation system) on the given image path.
    :param img_path: The image path to work with.
    :return: The Spotify playlist to send the client.
    :rtype: str
    """
    client_answer = ""

    try:
        client_answer = model_prediction.predict(img_path)

    except:
        print("Error: Could not fetch server's results.")
        exit()

    return client_answer


def main():
    try:
        print("Running AI")
        time.sleep(1)
        my_client_pipe = python_pipe.PipeClient("DebugCS")
        print("Receiving from client")
        left, img_path = my_client_pipe.read_message()

    except:
        print("Error: Could not reach the GUI. No image path available")
        exit()

    else:
        my_client_pipe.close_pipe()
        my_server_pipe = python_pipe.PipeServer("DebugPY")
        print("Sending to client")

        client_answer = activate_server(img_path)

        try:
            my_server_pipe.send_message(client_answer)

        except:
            print("Error: Could not send answers back to the GUI.")
            exit()

        else:
            my_server_pipe.close_pipe()


if __name__ == '__main__':
    main()
