import a0
import click
from . import _util


@click.group()
def cli():
    pass


@cli.command()
def ls():
    """List all topics with logs."""
    for topic in _util.detect_topics("log"):
        print(topic)


@cli.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("log"))
@click.option("--level",
              type=click.Choice(list(a0.LogLevel.__members__),
                                case_sensitive=False),
              default=a0.LogLevel.INFO.name,
              show_default=True)
@click.option("--init",
              type=click.Choice(list(a0.ReaderInit.__members__),
                                case_sensitive=False),
              default=a0.ReaderInit.AWAIT_NEW.name,
              show_default=True)
@click.option("--iter",
              type=click.Choice(list(a0.ReaderIter.__members__),
                                case_sensitive=False),
              default=a0.ReaderIter.NEXT.name,
              show_default=True)
@click.option("--count", "-n", type=click.INT)
@click.option("--duration", "-t", type=_util.ClickDuration())
def echo(topic, level, init, iter, count=None, duration=None):
    """Echo the messages logged on the given topic."""
    level = getattr(a0.LogLevel, level.upper())
    init = getattr(a0.ReaderInit, init.upper())
    iter = getattr(a0.ReaderIter, iter.upper())

    stream = _util.StreamHelper(count, duration)
    stream.install_sighandlers()

    ll = a0.LogListener(topic, level, init, iter,
                        lambda pkt: print(pkt.payload.decode()))

    stream.wait_shutdown()


@cli.command()
@click.argument("topic", shell_complete=_util.autocomplete_topics("log"))
def clear(topic):
    """Clear the log history for the given topic."""
    t = a0.Transport(a0.File(a0.env.topic_tmpl_log().format(topic=topic)))
    tlk = t.lock()
    tlk.clear()
