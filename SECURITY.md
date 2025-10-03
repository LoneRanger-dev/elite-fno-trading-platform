# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Elite FnO Trading Platform seriously. If you believe you have found a security vulnerability, please follow these steps:

1. **Do Not** disclose the vulnerability publicly
2. Send a detailed description to security@yourdomain.com including:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You can expect:

- Acknowledgment of your report within 24 hours
- Regular updates on the progress
- Credit for responsibly disclosing the issue

## Security Best Practices

When using this platform:

1. Always use secure API keys and tokens
2. Enable two-factor authentication
3. Regularly update dependencies
4. Monitor system logs for suspicious activities
5. Follow the principle of least privilege for API access

## Secure Configuration

Ensure your configuration follows these guidelines:

```python
# Use environment variables for sensitive data
KITE_API_KEY = os.environ.get('KITE_API_KEY')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
```

Never commit sensitive data to the repository.