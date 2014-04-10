# -*- coding: utf-8 -*-
"""
Pelican Comment System
======================

A Pelican plugin, which allows you to add comments to your articles.

Author: Bernhard Scheirle
"""

import logging
import os

logger = logging.getLogger(__name__)

from itertools import chain
from pelican import signals
from pelican.utils import strftime
from pelican.readers import MarkdownReader

import avatars

class Comment:
	def __init__(self, id, metadata, content, avatar):
		self.id = id
		self.content = content
		self.metadata = metadata
		self.replies = []
		self.avatar = avatar

	def addReply(self, comment):
		self.replies.append(comment)

	def getReply(self, id):
		for reply in self.replies:
			if reply.id == id:
				return reply
			else:
				deepReply = reply.getReply(id)
				if deepReply != None:
					return deepReply
		return None

	def __lt__(self, other):
		return self.metadata['date'] < other.metadata['date']

	def sortReplies(self):
		for r in self.replies:
			r.sortReplies()
		self.replies = sorted(self.replies)

	def countReplies(self):
		amount = 0
		for r in self.replies:
			amount += r.countReplies()
		return amount + len(self.replies)


def pelican_initialized(pelican):
	from pelican.settings import DEFAULT_CONFIG
	DEFAULT_CONFIG.setdefault('PELICAN_COMMENT_SYSTEM', False)
	DEFAULT_CONFIG.setdefault('PELICAN_COMMENT_SYSTEM_DIR' 'comments')
	DEFAULT_CONFIG.setdefault('PELICAN_COMMENT_SYSTEM_IDENTICON_OUTPUT_PATH' 'images/identicon')
	DEFAULT_CONFIG.setdefault('PELICAN_COMMENT_SYSTEM_IDENTICON_DATA', ())
	DEFAULT_CONFIG.setdefault('PELICAN_COMMENT_SYSTEM_IDENTICON_SIZE', 72)
	DEFAULT_CONFIG.setdefault('PELICAN_COMMENT_SYSTEM_AUTHORS', {})
	if pelican:
		pelican.settings.setdefault('PELICAN_COMMENT_SYSTEM', False)
		pelican.settings.setdefault('PELICAN_COMMENT_SYSTEM_DIR', 'comments')
		pelican.settings.setdefault('PELICAN_COMMENT_SYSTEM_IDENTICON_OUTPUT_PATH', 'images/identicon')
		pelican.settings.setdefault('PELICAN_COMMENT_SYSTEM_IDENTICON_DATA', ())
		pelican.settings.setdefault('PELICAN_COMMENT_SYSTEM_IDENTICON_SIZE', 72)
		pelican.settings.setdefault('PELICAN_COMMENT_SYSTEM_AUTHORS', {})


def initialize(article_generator):
	avatars.init(
		article_generator.settings['OUTPUT_PATH'],
		article_generator.settings['PELICAN_COMMENT_SYSTEM_IDENTICON_OUTPUT_PATH'],
		article_generator.settings['PELICAN_COMMENT_SYSTEM_IDENTICON_DATA'],
		article_generator.settings['PELICAN_COMMENT_SYSTEM_IDENTICON_SIZE']/3,
		article_generator.settings['PELICAN_COMMENT_SYSTEM_AUTHORS'],
		)

def add_static_comments(gen, metadata):
	if gen.settings['PELICAN_COMMENT_SYSTEM'] != True:
		return

	metadata['comments_count'] = 0
	metadata['comments'] = []

	if not 'slug' in metadata:
		logger.warning("pelican_comment_system: cant't locate comments files without slug tag in the article")
		return

	folder = os.path.join(gen.settings['PELICAN_COMMENT_SYSTEM_DIR'], metadata['slug'])

	if not os.path.isdir(folder):
		logger.debug("No comments found for: " + metadata['slug'])
		return

	reader = MarkdownReader(gen.settings)
	comments = []
	replies = []

	for file in os.listdir(folder):
		name, extension = os.path.splitext(file)
		if extension[1:].lower() in reader.file_extensions:
			content, meta = reader.read(os.path.join(folder, file))
			meta['locale_date'] = strftime(meta['date'], gen.settings['DEFAULT_DATE_FORMAT'])

			avatar_path = avatars.getAvatarPath(name, meta)
			com = Comment(name, meta, content, avatar_path)

			if 'replyto' in meta:
				replies.append( com )
			else:
				comments.append( com )

	#TODO: Fix this O(n²) loop
	for reply in replies:
		for comment in chain(comments, replies):
			if comment.id == reply.metadata['replyto']:
				comment.addReply(reply)

	count = 0
	for comment in comments:
		comment.sortReplies()
		count += comment.countReplies()

	comments = sorted(comments)

	metadata['comments_count'] = len(comments) + count
	metadata['comments'] = comments

def writeIdenticonsToDisk(gen, writer):
	avatars.generateAndSaveMissingAvatars()

def register():
	signals.initialized.connect(pelican_initialized)
	signals.article_generator_init.connect(initialize)
	signals.article_generator_context.connect(add_static_comments)
	signals.article_writer_finalized.connect(writeIdenticonsToDisk)
