# Jenkins with Docker Compose

This stack runs Jenkins locally in Docker and gives the Jenkins container access to the host Docker daemon so that the repository's Jenkinsfile can run tests, build the application image, and execute the container smoke test.

## Start Jenkins

```bash
docker compose up -d --build
```

Open:

```text
http://localhost:8080
```

## Get the initial admin password

```bash
docker exec dsoc-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Create the Assignment 5 Pipeline

1. Jenkins -> New Item -> Pipeline.
2. Select **Pipeline script from SCM**.
3. SCM: **Git**.
4. Repository URL:

```text
https://github.com/ernestajbatov-blip/distributed-soc-evidence-analyzer.git
```

5. Branch Specifier:

```text
*/main
```

6. Script Path:

```text
Jenkinsfile
```

7. Save and click **Build Now**.

Expected stages:

```text
Checkout -> Unit Tests -> Build Docker Image -> Container Smoke Test
```

## Stop Jenkins

```bash
docker compose down
```

To remove the persistent Jenkins data as well:

```bash
docker compose down -v
```

## Security note

The assignment configuration mounts `/var/run/docker.sock` into Jenkins and runs the Compose service as root so Jenkins can use Docker without host-specific group-ID configuration. This is convenient for an isolated classroom/lab machine, but it grants Jenkins high privileges over the Docker host. A production deployment should use isolated agents or a more restricted build architecture.
