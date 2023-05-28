import asyncio
from typing import AsyncGenerator
from uuid import uuid4, UUID
from aioconsole import ainput
from .struct import Message, Element, Identity, decode, encode


class UI:
    def __init__(self, host: str, port: int) -> None:
        self._id = uuid4()

        self._host = host
        self._port = port

        self._reader = None
        self._writer = None

        self._sender = None
        self._receiver = None

        self._messages: dict[UUID, Element] = {}

    async def start(self) -> None:
        await self._connect()

        try:
            await asyncio.gather(self._start_process_income_messages(), self._start_process_console())
        except Exit:
            pass

    async def _start_process_income_messages(self) -> None:
        async for message in self._read():
            self._messages[message.id] = message

    async def _start_process_console(self) -> None:
        while True:
            try:
                await self._process_console('Enter: ')
            except UserError as error:
                print(str(error))

    async def _process_console(self, title) -> None:
        value = await ainput(title)

        if not value:
            return

        if value.startswith(':'):
            await self._on_command(value)
        elif self._receiver and self._sender:
            await self._write(Message(sender=self._sender, receiver=self._receiver, value=value))
        else:
            raise UserError('Set "Sender" and "Receiver" if you want send message')

    async def _on_command(self, command: str) -> None:
        if '=' not in command:
            command += '='

        command, argument = (v.strip() for v in command.split('=', 1))

        match command:
            case ':quit' | ':q':
                raise Exit()
            case ':list' | ':l':
                for message in self._messages.values():
                    if isinstance(message, Message):
                        print(f'|<{message.sender}>: {message.time}|')
                        print(f'|{message.value}|')
                        print('.\n.\n.')
            case ':info' | ':i':
                print('Receiver:', self._receiver)
                print('Messages:', len(self._messages))
            case ':help' | ':h':
                print(
                    ':quit (:q) - Quit\r\n'
                    ':list (:l) - List all users\r\n'
                    ':user (:u) <user> - Authentication\r\n'
                    ':contact (:c) <user> - Set current contact'
                )
            case ':r' | ':receiver':
                if argument:
                    self._receiver = argument
            case ':s' | ':sender':
                if self._sender:
                    raise UserError(f'Already use: "{self._sender}"')

                if not argument:
                    raise UserError('Command argument is required')

                self._sender = argument

                await self._handshake()
            case _:
                print(f'What is this - {command}?')

    async def _read(self) -> AsyncGenerator[Element, None]:
        assert self._writer
        assert self._reader

        while not self._writer.is_closing():
            yield decode(await self._reader.readuntil(b'\0'))

    async def _write(self, element: Element, drain=False) -> None:
        assert self._writer

        self._writer.write(encode(element))

        if drain:
            await self._writer.drain()

    async def _connect(self) -> None:
        if self._writer:
            self._writer.close()

        self._reader = None
        self._writer = None

        try:
            reader, writer = await asyncio.open_connection(self._host, self._port)
        except OSError:
            raise

        self._reader = reader
        self._writer = writer

    async def _handshake(self) -> None:
        assert self._sender

        await self._write(Identity(
            id=self._id,
            sender=self._sender,
            receiver='none',
            password='none',
        ))


def open(host, port) -> None:
    asyncio.run(UI(host, port).start())


class Error(Exception):
    pass

class UserError(Error):
    pass

class Exit(Error):
    pass
