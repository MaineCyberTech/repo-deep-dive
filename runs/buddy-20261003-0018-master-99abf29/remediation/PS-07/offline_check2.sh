set -u
cd /srv/work/buddy
echo "=== build id in .next (alternate env build in place) ==="
cat .next/BUILD_ID
echo
echo "=== inlined env build id in client chunks ==="
grep -arl 'verify-abc123' .next/static | head -5 || echo NONE
echo "=== css google font refs (expect none) ==="
grep -arl 'fonts.googleapis.com' .next/static/css 2>/dev/null || echo NONE
echo "=== app server output google font refs (expect none) ==="
grep -arl 'fonts.googleapis.com' .next/server/app 2>/dev/null || echo NONE
echo "=== context of google ref in main chunk ==="
grep -ao '.\{70\}fonts.googleapis.com.\{40\}' .next/static/chunks/main-*.js 2>/dev/null | head -2 || echo NONE
echo "=== rendered HTML external font refs (expect 0) ==="
npx next start -p 3999 >/tmp/ps07-next2.log 2>&1 &
SRV=$!
sleep 8
curl -s http://127.0.0.1:3999/ > /tmp/ps07-page.html
grep -c 'fonts.googleapis.com' /tmp/ps07-page.html || true
echo "HTML bytes: $(wc -c < /tmp/ps07-page.html)"
kill $SRV 2>/dev/null
echo __CHECK2_DONE
