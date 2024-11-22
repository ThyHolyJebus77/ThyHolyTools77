@echo off

REM This batch script normalizes all MP3 files in a directory and its subdirectories.

REM Set the directory to process
for /r "C:\Users" %%i in (*.mp3) do (

  REM Display the file being processed
  echo Processing: "%%i"

  REM Normalize the audio file
  REM -t -12: Sets the target loudness to -12 LUFS
  REM -c:a libmp3lame: Uses the libmp3lame encoder for MP3 output
  REM -f: Forces overwriting of existing files
  REM --keep-loudness-range-target: Preserves the original loudness range of the audio
  REM -v: Enables verbose output for more detailed information during processing
  python -m ffmpeg_normalize "%%i" -o "%%i" -t -12 -c:a libmp3lame -f --keep-loudness-range-target -v -b:a 192k
)

pause

REM -------------------------------------------------------------------
REM Only additional options and what they would do:

REM -ar 44100: Sets the sample rate to 44.1 kHz
REM -b:a 192k: Sets the audio bitrate to 192 kbps
REM -tp -1: Sets the true peak limit to -1 dBTP
REM -lrt 10: Sets the loudness range target to 10 LU
REM --extract-format: Extracts the audio from a video file before normalizing
REM --normalization-type rms: Uses RMS-based normalization instead of EBU R128
REM -of aac: Sets the output format to AAC (requires specifying a different output file extension)
REM -ext m4a: Sets the output file extension to .m4a (useful when -of aac is used)
REM -------------------------------------------------------------------