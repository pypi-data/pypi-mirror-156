from pydeen.types import Auth
from pydeen.types import Backend
from pydeen.service import Service
from pydeen.http import HTTPBackend
import asyncio
import websockets


class WebSocketService(Service):

    def __init__(self, backend:HTTPBackend, client_id:str=""):
        super().__init__()
        self.type = "pydeen.WebSocketService"
        self.backend:HTTPBackend = backend
        self.quit_arrived = False
        self.websocket : websockets.websocket
        self.send_connect_msg = True
        self.headers = {}
        self.answer = None
        
        if self.client_id == "":
            self.client_id = self.generate_client_id()

    async def ws_listen(self):   
        # build url and authorization
        url = self.backend.get_property(Backend.BACKEND_PROP_URL)
        headers = self.headers
        if self.backend.is_auth_info_available() == True:
            auth_headers = self.backend.get_auth_info().get_auth_headers()
            print(headers, " - ", auth_headers)
            if auth_headers != None:
                headers = {**headers, **auth_headers}    
        print(headers)
        async with websockets.connect(url, extra_headers=headers) as websocket:
            # save my context
            self.websocket = websocket
            self.trace(f"Connected to Websocket: {url}")            
            self.trace(f"{len(self.actions)} actions and {len(self.commands)} are registered")

            # send 
            if self.send_connect_msg == True:
                connect_msg = "connect::" + self.client_id
                self.trace(f"> {connect_msg}")
                await websocket.send(connect_msg)
                self.send_connect_msg = False
            
            # wait for incoming messages
            while self.quit_arrived == False:
                response = await websocket.recv()
                self.trace(f"< {response}")

                handled = False    
                for action in self.actions:
                    self.answer = None
                    if action.parse(response) == True:
                        handled = True
                        self.trace(f"< action handler {type(action)} is valid for message")
                        if action.handle(response, self) == False:
                            self.trace(f"< action handler {type(action)} reports an error")
                        else:
                            self.trace(f"< action handler {type(action)} has handled the message")   
                            if self.answer != None and self.answer != "":
                                await websocket.send(self.answer)

                # not handled by registered handlers
                if handled == False:   
                    self.trace("< MESSAGE not handled by action handler!") 
                    
                    if response.lower() == "quit":
                        self.trace("< QUIT COMMAND ARRIVED")
                        self.stop()

                    #command = response
                    # payload = ""
                    # pos_sep = response.find("::")

                    # if  pos_sep > 0:
                    #     command = response[:pos_sep]
                    #     payload = response[pos_sep + 2:]
                    #     self.trace(f"< COMMAND detected: {command} payload = '{payload}'")

                    # if command == "quit":
                    #     self.trace("< QUIT COMMAND ARRIVED")
                    #     self.stop()
    async def send_text(self, text:str) -> bool:
        await self.websocket.send(text)
        return True

    def start(self) -> bool:
        if self.get_count_registered_actions() == 0:
            self.init_command_mode(echo=True)
        return True

    def stop(self) -> bool:
        self.quit_arrived = True
        return True

    def set_header(self, name:str, value:str):
        self.headers[name] = value

    def send_text(self, text) -> bool:
        self.answer = text
        return True

    def run(self) -> bool:
        try:
            # start sequence
            if self.start() == False:
                return False

            # start server
            asyncio.get_event_loop().run_until_complete(self.ws_listen())
            return True
        except KeyboardInterrupt:
            self.trace("Cancelled by user!")
        return True    