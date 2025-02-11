# pylint: disable=no-member
# pylint can't handle db.session
# pylint: disable=W0703
# W0703 -- too general exception -- don't really care
""" Fuctions for extracting data from database """
from flask_login import current_user
from models import Account, Ad, Channel, db


def get_all_accounts():
    """Returns all accounts stored in database"""
    accounts = Account.query.all()
    account_list = []
    for i in accounts:
        account_list.append(
            {
                "id": i.id,
                "username": i.username,
                "password": i.password,
                "email": i.email,
                "channel_owner": i.channel_owner,
            }
        )

    return account_list


def create_ad(title, topics="", text="", reward=0, show_in_list=True):
    """Creates new ad"""
    # there is an error here, current_user.id arg prolly should not be among the args
    new_ad = Ad(current_user.id, title, topics, text, reward, show_in_list)

    db.session.add(new_ad)
    db.session.commit()
    return does_ad_exist(title)


def does_ad_exist(ad_title):
    """Check if the ad with the given title exists in the database"""
    advertisement = Ad.query.filter_by(title=ad_title).first()
    return advertisement is not None


def create_channel(
    channel_name, topics, preferred_reward, subscribers=0, show_channel=True
):
    """Creates channel based on given args"""
    new_channel = Channel(
        current_user.id,
        show_channel,
        channel_name,
        subscribers,
        topics,
        preferred_reward,
    )

    db.session.add(new_channel)
    db.session.commit()
    return does_channel_exist(channel_name)


def does_channel_exist(channelname):
    """Check if the channel with the given name exists in the database"""
    channel = Channel.query.filter_by(channel_name=channelname).first()
    return channel is not None


def map_usernames(raw_accounts):
    """Create dictionary mapping accounts` ids and usernames"""
    accounts = {}
    for account in raw_accounts:
        accounts.update({account.id: account.username})
    return accounts


def get_channels(args):
    """Return ads data filtered according to the query"""
    if args.get("for") == "channelsPage":
        # return channels for channels page
        channels = Channel.query.filter_by(show_channel=True).all()
        accounts = map_usernames(Account.query.all())
        channels_data = []
        for channel in channels:
            try:
                channel.topics = channel.topics.split(",")
                channels_data.append(
                    {
                        "id": channel.id,
                        "ownerName": accounts[channel.owner_id],
                        "channelName": channel.channel_name,
                        "subscribers": channel.subscribers,
                        "topics": channel.topics,
                        "preferredReward": channel.preferred_reward,
                    }
                )
            except Exception:
                continue

        if args.get("id") is not None:
            searched_id = int(args.get("id"))
            channels_data = list(
                filter(lambda channel: channel["id"] == searched_id, channels_data)
            )
        if args.get("owner") is not None:
            searched_owner = args.get("owner")
            channels_data = list(
                filter(
                    lambda channel: searched_owner in channel["ownerName"],
                    channels_data,
                )
            )
        if args.get("name") is not None:
            searched_name = args.get("name")
            channels_data = list(
                filter(
                    lambda channel: searched_name in channel["channelName"],
                    channels_data,
                )
            )
        if args.get("subs") is not None:
            min_subs = int(args.get("subs"))
            channels_data = list(
                filter(
                    lambda channel: channel["subscribers"] >= min_subs,
                    channels_data,
                )
            )
        if args.get("topics") is not None:
            topics = args.get("topics")
            channels_data = list(
                filter(
                    lambda channel: topics in channel["topics"],
                    channels_data,
                )
            )
        if args.get("reward") is not None:
            max_reward = int(args.get("reward"))
            channels_data = list(
                filter(
                    lambda channel: channel["preferredReward"] <= max_reward,
                    channels_data,
                )
            )

        for channel in channels_data:
            channel["topics"] = (", ").join(channel["topics"])

        return channels_data

    return None


def get_all_channels():
    """Returns JSON of all channels on site"""
    channels = Channel.query.all()
    channel_list = []
    for i in channels:
        channel_list.append(
            {
                "owner_id": i.owner_id,
                "show_channel": i.show_channel,
                "channel_name": i.channel_name,
                "subscribers": i.subscribers,
                "topics": i.topics,
                "preferred_reward": i.preferred_reward,
            }
        )

    return channel_list


def get_channels_by_topic(topic):
    """Returns channels with given topic"""
    channels = Channel.query.all()
    channel_list = []
    for i in channels:
        topic_list = i.topics.split(
            ","
        )  ## assumes topics are seperated by a single comment(no spaces) e.g. "Tech,Fashion,Misc"
        if topic in topic_list:
            channel_list.append(
                {
                    "owner_id": i.owner_id,
                    "show_channel": i.show_channel,
                    "channel_name": i.channel_name,
                    "subscribers": i.subscribers,
                    "topics": i.topics,
                    "preferred_reward": i.preferred_reward,
                }
            )

    return channel_list


def get_channels_by_sub_count(
    min_sub_count,
):
    """returns all channels with subscriber count above or equal to a minimum subscriber count"""
    channels = Channel.query.all()
    channel_list = []
    for i in channels:
        channel_sub_count = (
            i.subscribers
        )  ## assumes topics are seperated by a single comment(no spaces) e.g. "Tech,Fashion,Misc"
        if channel_sub_count >= min_sub_count:
            channel_list.append(
                {
                    "owner_id": i.owner_id,
                    "show_channel": i.show_channel,
                    "channel_name": i.channel_name,
                    "subscribers": i.subscribers,
                    "topics": i.topics,
                    "preferred_reward": i.preferred_reward,
                }
            )

    return channel_list


def get_channels_by_owner_username(ownername):
    """returns all channels owned by user with the given username"""
    user = Account.query.filter_by(username=ownername).first()
    channels = Channel.query.filter_by(owner_id=user.id).all()
    channel_list = []
    for i in channels:
        channel_list.append(
            {
                "owner_id": i.owner_id,
                "show_channel": i.show_channel,
                "channel_name": i.channel_name,
                "subscribers": i.subscribers,
                "topics": i.topics,
                "preferred_reward": i.preferred_reward,
            }
        )

    return channel_list


def get_channels_by_owner_email(owner_email):
    """returns all channels owned by user with the given email"""
    user = Account.query.filter_by(username=owner_email).first()
    channels = Channel.query.filter_by(owner_id=user.id).all()
    channel_list = []
    for i in channels:
        channel_list.append(
            {
                "owner_id": i.owner_id,
                "show_channel": i.show_channel,
                "channel_name": i.channel_name,
                "subscribers": i.subscribers,
                "topics": i.topics,
                "preferred_reward": i.preferred_reward,
            }
        )

    return channel_list


def get_ads(args):
    """Return ads data filtered according to the query"""
    ads_data = []
    if args.get("for") == "adsPage":
        ads = Ad.query.filter_by(show_in_list=True).all()
        accounts = map_usernames(Account.query.all())
        for advertisement in ads:
            try:
                advertisement.topics = advertisement.topics.split(",")
                ads_data.append(
                    {
                        "id": advertisement.id,
                        "creatorName": accounts[advertisement.creator_id],
                        "title": advertisement.title,
                        "topics": advertisement.topics,
                        "text": advertisement.text,
                        "reward": advertisement.reward,
                    }
                )
            except Exception:
                continue
        if args.get("id") is not None:
            searched_id = int(args.get("id"))
            ads_data = list(
                filter(
                    lambda advertisement: advertisement["id"] == searched_id, ads_data
                )
            )
        if args.get("creator") is not None:
            searched_creator = args.get("creator")
            ads_data = list(
                filter(
                    lambda advertisement: searched_creator
                    in advertisement["creatorName"],
                    ads_data,
                )
            )
        if args.get("title") is not None:
            searched_title = args.get("title")
            ads_data = list(
                filter(
                    lambda advertisement: searched_title in advertisement["title"],
                    ads_data,
                )
            )
        if args.get("topics") is not None:
            searched_topics = args.get("topics")
            ads_data = list(
                filter(
                    lambda advertisement: searched_topics in advertisement["topics"],
                    ads_data,
                )
            )
        if args.get("text") is not None:
            searched_text = args.get("text")
            ads_data = list(
                filter(
                    lambda advertisement: searched_text in advertisement["text"],
                    ads_data,
                )
            )
        if args.get("reward") is not None:
            max_reward = int(args.get("reward"))
            ads_data = list(
                filter(
                    lambda advertisement: advertisement["reward"] <= max_reward,
                    ads_data,
                )
            )

        for advertisement in ads_data:
            advertisement["topics"] = (", ").join(advertisement["topics"])

        return ads_data

    return ads_data


def get_all_ads():
    """Return all ads data"""
    ads = Ad.query.all()
    ads_list = []
    for i in ads:
        ads_list.append(
            {
                "creator_id": i.creator_id,
                "title": i.title,
                "topics": i.topics,
                "text": i.text,
                "reward": i.reward,
                "show_in_list": i.show_in_list,
            }
        )

    return ads_list


def get_ads_by_topic(topic):
    """Return ads with given topics"""
    ads = Ad.query.all()
    ads_list = []
    for i in ads:
        topic_list = i.topics.split(
            ","
        )  ## assumes topics are seperated by a single comment(no spaces) e.g. "Tech,Fashion,Misc"
        if topic in topic_list:
            ads_list.append(
                {
                    "creator_id": i.creator_id,
                    "title": i.title,
                    "topics": i.topics,
                    "text": i.text,
                    "reward": i.reward,
                    "show_in_list": i.show_in_list,
                }
            )

    return ads_list


def get_ads_by_owner_username(ownername):
    """Returns ads of the user with given username"""
    user = Account.query.filter_by(username=ownername).first()
    ads = Ad.query.filter_by(creator_id=user.id).all()
    ads_list = []
    for i in ads:
        ads_list.append(
            {
                "creator_id": i.creator_id,
                "title": i.title,
                "topics": i.topics,
                "text": i.text,
                "reward": i.reward,
                "show_in_list": i.show_in_list,
            }
        )

    return ads_list


def get_ads_by_owner_email(owner_email):
    """Return ads of the user with given email"""
    user = Account.query.filter_by(username=owner_email).first()
    ads = Ad.query.filter_by(creator_id=user.id).all()
    ads_list = []
    for i in ads:
        ads_list.append(
            {
                "creator_id": i.creator_id,
                "title": i.title,
                "topics": i.topics,
                "text": i.text,
                "reward": i.reward,
                "show_in_list": i.show_in_list,
            }
        )

    return ads_list


def delete_all_ads():
    """Deletes all ads"""
    rows_deleted = Ad.query.delete()
    db.session.commit()
    return rows_deleted


def delete_all_channels():
    """Deletes all channels"""
    rows_deleted = Channel.query.delete()
    db.session.commit()
    return rows_deleted


def delete_all_account():
    """Deletes all accounts"""
    rows_deleted = Account.query.delete()
    db.session.commit()
    return rows_deleted


def delete_ad(ad_id):
    """Deletes the add with given id"""
    if ad_id is None:
        return -1
    rows_deleted = Ad.query.filter_by(id=ad_id).delete()
    db.session.commit()
    return rows_deleted


def delete_channel(channel_id):
    """Deletes the channel with given id"""
    if channel_id is None:
        return -1
    rows_deleted = Channel.query.filter_by(id=channel_id).delete()
    db.session.commit()
    return rows_deleted


def delete_account(account_id):
    """Deletes the account with given id"""
    if account_id is None:
        return -1
    rows_deleted = Account.query.filter_by(id=account_id).delete()
    db.session.commit()
    return rows_deleted
