from func.supabase import supabase

from disnake.ext import commands
from disnake import Member, Spotify, ActivityType


class OnPresenceUpdate(commands.Cog):
    def __init__(self, client):
        """User updates their username or avatar, we update that in the database."""
        self.client = client

    @commands.Cog.listener()
    async def on_presence_update(self, before: Member, after: Member):

        if before.id != 210471447649320970:
            return

        db_data = {
            'id': after.id,
            'status': str(after.status),
            'spotify': {},
            'playing': [],
            'custom': [],
        }

        for activity in after.activities:
            if isinstance(activity, Spotify):
                party_id = activity.party_id
                party_id = party_id.split(':')[-1] if party_id else None

                db_data['spotify'] = {
                    'album_cover_url': activity.album_cover_url,
                    'track_id': activity.track_id, # url - f"https://open.spotify.com/track/{self.track_id}"
                    'title': activity.title,
                    'artist': activity.artist,
                    'duration': activity.duration.total_seconds(),
                    'party_id': party_id,
                }
            # elif activity.type == ActivityType.playing:
            #     db_data['playing'].append({
            #         'name': activity.name,
            #         'state': activity.state,
            #         'start': activity.start.timestamp() if activity.start else None,
            #         'details': activity.details if hasattr(activity, 'details') else None,
            #         'platform': activity.platform if hasattr(activity, 'platform') else None,
            #     })
            # elif activity.type == ActivityType.custom:
            #     db_data['custom'].append({
            #         'name': activity.name,
            #         'emoji_url': activity.emoji.url if activity.emoji else None,
            #         'emoji_name': activity.emoji.name if activity.emoji else None,
            #         'small_image_link': activity.small_image_url if hasattr(activity, 'small_image_url') else None,
            #     })

        supabase.from_('presences').upsert(db_data).execute()


def setup(client):
    client.add_cog(OnPresenceUpdate(client))
