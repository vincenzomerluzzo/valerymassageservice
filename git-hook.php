<?php
// Simple GitHub webhook handler for cPanel deployment
// - Place this file in a public directory (e.g. public_html/git-hook.php)
// - Configure a GitHub webhook pointing to its URL
// - Optionally set a secret and copy it to $secret below
// - Give the web user permission to run `git pull` in the repo
//   (usually the repo lives in ~/public_html or a sibling folder)

// configuration -------------------------------------------------------------
$repoDir = getenv('HOME') . '/public_html'; // adjust if your repository is elsewhere
$branch  = 'main';
$secret  = ''; // copy the webhook secret here, if you set one on GitHub

// read the request body and signature
$rawPayload = file_get_contents('php://input');
$signature  = $_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '';

if ($secret !== '' && $signature !== '') {
    $hash = 'sha256=' . hash_hmac('sha256', $rawPayload, $secret);
    if (!hash_equals($hash, $signature)) {
        header('HTTP/1.1 403 Forbidden');
        echo "Invalid signature\n";
        exit;
    }
}

// decode payload
$payload = json_decode($rawPayload, true);
if (!$payload) {
    header('HTTP/1.1 400 Bad Request');
    echo "Invalid JSON\n";
    exit;
}

// only deploy on push to the configured branch
if (isset($payload['ref']) && $payload['ref'] === "refs/heads/$branch") {
    chdir($repoDir);
    // fetch latest and reset; keep working copy clean
    shell_exec('git fetch origin '.escapeshellarg($branch).' 2>&1');
    shell_exec('git reset --hard origin/'.escapeshellarg($branch).' 2>&1');

    // optionally, run any build steps from .cpanel.yml or npm
    // e.g. shell_exec('npm install && npm run build');

    echo "Deployment to $repoDir complete\n";
} else {
    echo "No deployment: ref did not match $branch\n";
}
