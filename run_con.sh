set -o errexit

(cd local-runner; ./local-runner-console.sh)&
sleep 0.5
(cd replay_utils; time python3 -B run.py)

cat local-runner/result.txt
