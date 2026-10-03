set -u
cd /srv/work/buddy
echo "=== current build id ==="
cat .next/BUILD_ID
echo "=== sw registration build id in bundle ==="
grep -arho 'sw.js?v=[A-Za-z0-9._-]*' .next/static | sort -u
echo "=== third-party font refs in build (expect none) ==="
grep -arl 'fonts.googleapis.com\|fonts.gstatic.com' .next || echo NONE
echo "=== local font files ==="
ls .next/static/media | head -4
echo "=== cache name logic in public/sw.js ==="
grep -n 'buddy-cache' public/sw.js
echo "=== alternate build id rebuild ==="
NEXT_PUBLIC_BUILD_ID=verify-abc123 npm run build >/tmp/ps07-build2.log 2>&1
cat .next/BUILD_ID
grep -arho 'sw.js?v=[A-Za-z0-9._-]*' .next/static | sort -u
echo __OFFLINE_DONE
