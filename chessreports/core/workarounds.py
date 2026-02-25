# workarounds.py
# Copyright 2026 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess reports database workarounds."""

# Supplied on 25 February 2026 by
# Membership Support <membership.tech@englishchess.org.uk>
# in response to my report of being unable to download required information
# from the ECF Rating Database earlier on same day.
# The HTTP Error 403 : Forbidden is associated with error code 1010 which
# is a known Cloudflare behaviour.
# The workaround is supply an acceptable User-Agent in the request headers.
# Thanks to Dave Thomas.
# Used by all urllib.request.urlopen() calls.
url_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3)"}
