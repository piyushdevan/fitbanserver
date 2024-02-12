try:
                    conn.sendall(b"Data received by server")
                except ConnectionAbortedError:
                    print("Connection aborted by the client")
                    break