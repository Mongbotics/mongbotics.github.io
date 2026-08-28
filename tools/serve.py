"""Static server for local preview that can actually stream video.

python3 -m http.server is single threaded, speaks HTTP/1.0 (no keep-alive) and
ignores Range requests. A <video> element then sits in networkState LOADING
forever. This adds threads, HTTP/1.1 and 206 partial responses.

It also sends no-store, so an edited stylesheet always reloads.

GitHub Pages does the first three already, so this is only needed locally.
"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class RangeHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"          # keep-alive, which media playback needs

    def send_head(self):
        rng = self.headers.get('Range')
        if not rng:
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404)
            return None

        size = os.fstat(f.fileno()).st_size
        m = re.match(r'bytes=(\d*)-(\d*)$', rng.strip())
        if not m:
            f.close()
            self.send_error(400)
            return None

        start = int(m.group(1)) if m.group(1) else 0
        end = int(m.group(2)) if m.group(2) else size - 1
        end = min(end, size - 1)
        if start > end:
            f.close()
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None

        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        f.seek(start)
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, '_remaining', None)
        if left is None:
            return super().copyfile(source, outputfile)
        try:
            while left > 0:
                chunk = source.read(min(64 * 1024, left))
                if not chunk:
                    break
                outputfile.write(chunk)
                left -= len(chunk)
        finally:
            self._remaining = None

    def end_headers(self):
        # Chrome has no expiry to go on without this, so it guesses, and it
        # guesses "keep the old styles.css". That has repeatedly made correct
        # CSS edits look like they did nothing. Never cache anything locally.
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, *a):
        pass


os.chdir(sys.argv[1])
print("serving", sys.argv[1], "on http://localhost:8765", flush=True)
ThreadingHTTPServer(('127.0.0.1', 8765), RangeHandler).serve_forever()
