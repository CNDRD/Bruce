import yaml, datetime

config = yaml.safe_load(open('config.yml'))
clv = config.get('console_logging')

def cl(ctx, cog=None, event=None):
    if not clv:
        return
    if event is None and cog is None:
        print(f'{ctx.command.cog_name} // {ctx.command.name} @ {datetime.datetime.now()}')
    else:
        print(f'{cog} // {event} @ {datetime.datetime.now()}')
