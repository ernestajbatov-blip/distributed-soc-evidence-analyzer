# Jenkins setup for Assignment 5

The repository contains a Declarative `Jenkinsfile` with four stages:

1. Checkout source from GitHub.
2. Run unit tests in a temporary Python 3.13 container.
3. Build the application Docker image.
4. Run a smoke test and require `overall_pass: true`.

## Jenkins node requirements

- Jenkins 2.x or later with Pipeline support.
- Git installed and access to this public repository.
- Docker Engine and Docker CLI available to the Jenkins agent.
- The Jenkins service account must be allowed to access the Docker daemon.

## Create the Pipeline

1. Jenkins Dashboard -> New Item -> Pipeline.
2. Select **Pipeline script from SCM**.
3. SCM: Git.
4. Repository URL: `https://github.com/ernestajbatov-blip/distributed-soc-evidence-analyzer.git`.
5. Branch: `*/main`.
6. Script Path: `Jenkinsfile`.
7. Save and select **Build Now**.

Expected successful stages: Checkout -> Unit Tests -> Build Docker Image -> Container Smoke Test.

## Security note

Access to `/var/run/docker.sock` effectively grants high privileges on the host. For a classroom/lab environment this may be acceptable, but production Jenkins should use isolated build agents and tighter daemon access controls.
