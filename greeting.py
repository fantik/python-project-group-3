from rich import print as rprint

_ROBOT_ART = r"""

               [yellow]●[/yellow]  [yellow]●[/yellow]       [white].-~~~~-.[/white]
               [yellow]│[/yellow]  [yellow]│[/yellow]      [white]|[/white]   {bubble}  [white]|[/white]
             [white][red]ᐱ[/red] ~~~ [red]ᐱ[/red][/white]      [white]'-~~~~-'[/white]
           [white]／[/white] [bold cyan]◕[/bold cyan]   [bold cyan]◕[/bold cyan] [white]＼[/white]
           [white]│[/white] [red]*[/red] [bold cyan] ͜‿͜ [/bold cyan] [red]*[/red] [white]│[/white]
           [white]＼[/white]       [white]／[/white]
            [white](-~~~~~-)[/white]
      {footer}
"""


def print_welcome_banner():
    """Cute robot with a speech bubble on the right side."""
    rprint(
        _ROBOT_ART.format(
            bubble="[green]HI![/green]",
            footer=(
                "[bold cyan]Personal Assistant[/bold cyan] "
                "[red]— ready to help[/red] [red]❤️[/red]"
            ),
        )
    )


def print_goodbye_banner():
    """Same robot waving bye on exit."""
    rprint(
        _ROBOT_ART.format(
            bubble="[green]BYE[/green]",
            footer=(
                "[bold cyan]Personal Assistant[/bold cyan] "
                "[red]— see you next time[/red] [red]❤️[/red]"
            ),
        )
    )
