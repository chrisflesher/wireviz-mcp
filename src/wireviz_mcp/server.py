"""Hello World MCP Server using FastMCP."""

import typing

import asyncio
import fastmcp

mcp = fastmcp.FastMCP('Hello World MCP Server')


@mcp.tool()
def say_hello(name: str = 'World') -> str:
    """
    Say hello to someone.

    Args:
        name: The name of the person to greet (default: 'World')

    Returns:
        A greeting message
    """
    return f'Hello, {name}! This is a greeting from the MCP server.'


@mcp.tool()
def get_server_info() -> typing.Dict[str, typing.Any]:
    """
    Get information about this MCP server.

    Returns:
        Dictionary containing server information
    """
    return {
        'name': 'Hello World MCP Server',
        'version': '0.1.0',
        'description': 'A simple Hello World MCP server using FastMCP',
        'tools': ['say_hello', 'get_server_info'],
        'author': 'Your Name'
    }


@mcp.tool()
def echo_message(message: str) -> str:
    """
    Echo back a message.

    Args:
        message: The message to echo back

    Returns:
        The same message that was sent
    """
    return f'Echo: {message}'


@mcp.tool()
def count_words(text: str) -> typing.Dict[str, typing.Any]:
    """
    Count words in a given text.

    Args:
        text: The text to analyze

    Returns:
        Dictionary with word count statistics
    """
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = len(text.replace(' ', ''))

    return {
        'text': text,
        'word_count': word_count,
        'character_count': char_count,
        'character_count_no_spaces': char_count_no_spaces,
        'words': words
    }


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
