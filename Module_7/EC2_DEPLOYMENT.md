# EC2 Deployment Log

## Deployment Steps
1. **SSH into EC2:** Connected via `ssh -i "your-key.pem" ec2-user@3.144.21.196`.
2. **Environment Setup:** Installed Docker and Docker Compose on the Amazon Linux 2023 instance.
3. **Container Configuration:** Created `docker-compose.ec2.yml` using the images pushed to Docker Hub (`masaomienami/module_6:v1-web` and `v1-worker`).
4. **Execution:** Ran the stack using:
   ```bash
   docker compose -f docker-compose.ec2.yml up -d

Troubleshooting Notes

    YAML Formatting: Encountered "did not find expected '-' indicator" errors during file creation. This was resolved by using a cat << 'EOF' "Here Doc" to ensure proper indentation and line breaks were preserved during the SSH session.

    Image Access: Initially faced "access denied" errors. Resolved by ensuring Docker Hub repositories were public and tagging images with specific version tags (v1-web) rather than using the default latest.

    Security Groups: Manually opened Port 8080 in the AWS Security Group to allow external traffic to reach the Flask Web UI.