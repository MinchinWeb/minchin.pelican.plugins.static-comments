# -*- coding: utf-8 -*-
"""
Pelican Static Comment System
======================

A Pelican plugin, which allows you to add static comments to your articles.

Creator: Bernhard Scheirle
Maintainer: William Minchin
"""
from __future__ import unicode_literals

import copy
import logging
import os

logger = logging.getLogger(__name__)

from itertools import chain

from pelican import signals
from pelican.readers import Readers
from pelican.writers import Writer

from . import avatars
from .comment import Comment

# fmt: off
__version__ = "2.1.3-dev"
__title__ = "minchin.pelican.plugins.static-comments"
__description__ = "A Pelican plugin, which allows you to add static comments to your articles."
__author__ = "William Minchin"
__email__ = "w_minchin@hotmail.com"
__url__ = "https://github.com/MinchinWeb/minchin.pelican.plugins.static_comments"
__license__ = "GPLv3+"
# fmt: on

LOG_PREFIX = "[Static Comments]"

_all_comments = []
_pelican_writer = None
_pelican_obj = None


def setdefault(pelican, settings):
    from pelican.settings import DEFAULT_CONFIG

    for key, value in settings:
        DEFAULT_CONFIG.setdefault(key, value)

    if not pelican:
        return

    for key, value in settings:
        pelican.settings.setdefault(key, value)


def pelican_initialized(pelican):
    from pelican.settings import DEFAULT_CONFIG

    settings = [
        ("PELICAN_COMMENT_SYSTEM", False),
        ("PELICAN_COMMENT_SYSTEM_DIR", "comments"),
        ("PELICAN_COMMENT_SYSTEM_IDENTICON_OUTPUT_PATH", "images/identicon"),
        ("PELICAN_COMMENT_SYSTEM_IDENTICON_DATA", ()),
        ("PELICAN_COMMENT_SYSTEM_IDENTICON_SIZE", 72),
        ("PELICAN_COMMENT_SYSTEM_AUTHORS", {}),
        ("PELICAN_COMMENT_SYSTEM_FEED", os.path.join("feeds", "comment.%s.atom.xml")),
        (
            "PELICAN_COMMENT_SYSTEM_FEED_ALL",
            os.path.join("feeds", "comments.all.atom.xml"),
        ),
        ("COMMENT_URL", "#comment-{slug}"),
    ]

    setdefault(pelican, settings)

    DEFAULT_CONFIG["PAGE_EXCLUDES"].append(DEFAULT_CONFIG["PELICAN_COMMENT_SYSTEM_DIR"])
    DEFAULT_CONFIG["ARTICLE_EXCLUDES"].append(
        DEFAULT_CONFIG["PELICAN_COMMENT_SYSTEM_DIR"]
    )
    pelican.settings["PAGE_EXCLUDES"].append(
        pelican.settings["PELICAN_COMMENT_SYSTEM_DIR"]
    )
    pelican.settings["ARTICLE_EXCLUDES"].append(
        pelican.settings["PELICAN_COMMENT_SYSTEM_DIR"]
    )

    global _pelican_obj
    _pelican_obj = pelican


def initialize(article_generator):
    avatars.init(
        article_generator.settings["OUTPUT_PATH"],
        article_generator.settings["PELICAN_COMMENT_SYSTEM_IDENTICON_OUTPUT_PATH"],
        article_generator.settings["PELICAN_COMMENT_SYSTEM_IDENTICON_DATA"],
        article_generator.settings["PELICAN_COMMENT_SYSTEM_IDENTICON_SIZE"] / 3,
        article_generator.settings["PELICAN_COMMENT_SYSTEM_AUTHORS"],
    )

    # Reset old states (autoreload mode)
    global _all_comments
    global _pelican_writer
    try:
        # Pelican 4.5.2 and newer
        # see https://github.com/getpelican/pelican/commit/afdf0fb3cf6cd376a6f241e2d5bbf99cf0e348c2
        _pelican_writer = _pelican_obj._get_writer()
    except AttributeError:
        _pelican_writer = _pelican_obj.get_writer()
    _all_comments = []


def warn_on_slug_collision(items):
    slugs = {}
    for comment in items:
        if comment.slug not in slugs:
            slugs[comment.slug] = [comment]
        else:
            slugs[comment.slug].append(comment)

    for slug, itemList in slugs.items():
        len_ = len(itemList)
        if len_ > 1:
            logger.warning(
                "%s There are %s comments with the same slug: %s"
                % (LOG_PREFIX, len_, slug)
            )
            for x in itemList:
                logger.warning("%s    %s" % (LOG_PREFIX, x.source_path))


def write_feed_all(gen, writer):
    if gen.settings["PELICAN_COMMENT_SYSTEM"] is not True:
        return
    if gen.settings["PELICAN_COMMENT_SYSTEM_FEED_ALL"] is None:
        return

    context = copy.copy(gen.context)
    context["SITENAME"] += " - All Comments"
    context["SITESUBTITLE"] = ""
    path = gen.settings["PELICAN_COMMENT_SYSTEM_FEED_ALL"]

    global _all_comments
    _all_comments = sorted(_all_comments)
    _all_comments.reverse()

    for com in _all_comments:
        com.title = com.article.title + " - " + com.title
        com.override_url = com.article.url + com.url

    writer.write_feed(_all_comments, context, path)


def write_feed(gen, items, context, slug):
    if gen.settings["PELICAN_COMMENT_SYSTEM_FEED"] is None:
        return

    path = gen.settings["PELICAN_COMMENT_SYSTEM_FEED"] % slug
    _pelican_writer.write_feed(items, context, path)


def process_comments(article_generator):
    for article in article_generator.articles:
        add_static_comments(article_generator, article)


def mirror_to_translations(article):
    for translation in article.translations:
        translation.comments_count = article.comments_count
        translation.comments = article.comments


def add_static_comments(gen, content):
    if gen.settings["PELICAN_COMMENT_SYSTEM"] is not True:
        return

    global _all_comments

    content.comments_count = 0
    content.comments = []
    mirror_to_translations(content)

    # Modify the local context, so we get proper values for the feed
    context = copy.copy(gen.context)
    context["SITEURL"] += "/" + content.url
    context["SITENAME"] += " - Comments: " + content.title
    context["SITESUBTITLE"] = ""

    folder = os.path.join(
        gen.settings["PATH"], gen.settings["PELICAN_COMMENT_SYSTEM_DIR"], content.slug
    )

    if not os.path.isdir(folder):
        logger.debug("%s No comments found for: %s" % (LOG_PREFIX, content.slug))
        write_feed(gen, [], context, content.slug)
        return

    reader = Readers(gen.settings)
    comments = []
    replies = []

    for file in os.listdir(folder):
        name, extension = os.path.splitext(file)
        if extension[1:].lower() in reader.extensions:
            com = reader.read_file(
                base_path=folder, path=file, content_class=Comment, context=context
            )

            com.article = content
            _all_comments.append(com)

            if hasattr(com, "replyto"):
                replies.append(com)
            else:
                comments.append(com)

    feed_items = sorted(comments + replies)
    feed_items.reverse()
    warn_on_slug_collision(feed_items)

    write_feed(gen, feed_items, context, content.slug)

    # TODO: Fix this O(n²) loop
    for reply in replies:
        found_parent = False
        for comment in chain(comments, replies):
            if comment.slug == reply.replyto:
                comment.addReply(reply)
                found_parent = True
                break
        if not found_parent:
            logger.warning(
                '%s Comment "%s/%s" is a reply to non-existent '
                'comment "%s". Make sure the replyto attribute is '
                "set correctly." % (LOG_PREFIX, content.slug, reply.slug, reply.replyto)
            )

    count = 0
    for comment in comments:
        comment.sortReplies()
        count += comment.countReplies()

    comments = sorted(comments)

    content.comments_count = len(comments) + count
    content.comments = comments
    mirror_to_translations(content)


def writeIdenticonsToDisk(gen, writer):
    avatars.generateAndSaveMissingAvatars()


def pelican_finalized(pelican):
    if pelican.settings["PELICAN_COMMENT_SYSTEM"] is not True:
        return
    global _all_comments
    print(
        "%s Processed %s comment%s."
        % (LOG_PREFIX, len(_all_comments), "s" if len(_all_comments) != 1 else "")
    )


def register():
    signals.initialized.connect(pelican_initialized)
    signals.article_generator_init.connect(initialize)
    signals.article_generator_finalized.connect(process_comments)
    signals.article_writer_finalized.connect(writeIdenticonsToDisk)
    signals.article_writer_finalized.connect(write_feed_all)
    signals.finalized.connect(pelican_finalized)
