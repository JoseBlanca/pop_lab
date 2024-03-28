import subprocess

cmd = [
    "jupyter",
    "lite",
    "build",
    "--contents",
    "src/pop_lab",
    "--output-dir",
    "output_site",
]
subprocess.run(cmd, check=True)

cmd = ["jupyter", "lite", "serve", "--output-dir", "output_site"]
subprocess.run(cmd, check=True)
