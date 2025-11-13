# Contributing to Balboa GS500Z Integration

Thank you for your interest in contributing to the Balboa GS500Z Home Assistant integration! This document provides guidelines and information for contributors.

## 🎯 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**:
  - Home Assistant version
  - Integration version
  - EW11A firmware version
  - GS500Z firmware version (if known)
- **Logs**: Relevant logs with debug enabled
- **Screenshots**: If applicable

#### Example Bug Report

```markdown
**Description**
The climate entity shows unavailable after Home Assistant restart.

**Steps to Reproduce**
1. Install integration
2. Configure EW11A at 192.168.1.100:8899
3. Restart Home Assistant
4. Check climate.spa entity

**Expected Behavior**
Entity should reconnect automatically.

**Actual Behavior**
Entity remains unavailable until integration is reloaded.

**Environment**
- HA Version: 2024.1.0
- Integration Version: 1.0.0
- EW11A: Firmware 3.5

**Logs**
```
[See attached logs]
```
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Use case**: Why is this enhancement needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other solutions you've considered
- **Additional context**: Screenshots, examples, etc.

### Protocol Documentation

If you've discovered new details about the RS-485 protocol:

1. **Capture raw frames**: Use an RS-485 analyzer or the integration's debug logs
2. **Document the behavior**: What action caused these frames?
3. **Provide examples**: Multiple frame examples are helpful
4. **Test your findings**: Verify the behavior is consistent

Example contribution:

```markdown
## New Discovery: Pump Control

I've discovered that byte 12 controls the pump state.

**Frame examples:**
- Pump OFF: `[643F2B...00...]` (byte 12 = 0x00)
- Pump ON:  `[643F2B...01...]` (byte 12 = 0x01)

**Test method:**
1. Pressed pump button on VL403
2. Observed byte 12 change from 0x00 to 0x01
3. Confirmed with multiple tests

**Frames captured:**
[Attach pcap file or hex dumps]
```

## 🔧 Development Setup

### Prerequisites

- Python 3.11+
- Home Assistant development environment
- Git

### Setting Up Development Environment

1. **Fork the repository**

```bash
git clone https://github.com/YOUR-USERNAME/Balboa-GS500z.git
cd Balboa-GS500z
```

2. **Create a branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

3. **Install in development mode**

Copy to your HA custom_components:

```bash
ln -s $(pwd)/custom_components/balboa_gs500z ~/.homeassistant/custom_components/
```

4. **Enable debug logging**

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
```

5. **Restart Home Assistant**

```bash
ha core restart
```

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and small

Example:

```python
def parse_temperature(raw_value: int) -> int:
    """
    Parse raw temperature value from RS-485 frame.

    Args:
        raw_value: Raw byte value (0-255)

    Returns:
        Temperature in Celsius (rounded to nearest integer)
    """
    return round(raw_value * 0.5)
```

### Testing Your Changes

1. **Manual testing**:
   - Test all affected features
   - Test error conditions
   - Test with different configurations

2. **Check logs**:
   - No errors should appear
   - Debug logs should be informative
   - No excessive logging at info level

3. **Test integration reload**:
   - Settings → Devices & Services → Balboa GS500Z → Reload

4. **Test Home Assistant restart**:
   - Verify reconnection works

### Commit Messages

Use clear, descriptive commit messages:

```
Add pump control support

- Parse byte 12 for pump state
- Add binary_sensor for pump
- Update documentation with pump protocol details
```

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## 📝 Pull Request Process

1. **Update documentation**:
   - Update README.md if needed
   - Update PROTOCOL.md for protocol changes
   - Add examples to EXAMPLES.md if applicable
   - Update CHANGELOG.md

2. **Test thoroughly**:
   - Test all changes
   - Verify no regressions
   - Test on a real spa if possible

3. **Create pull request**:
   - Use a clear title
   - Reference related issues
   - Describe your changes
   - Include test results

4. **Respond to feedback**:
   - Address review comments
   - Update PR as needed
   - Be patient and respectful

### Pull Request Template

```markdown
## Description
[Clear description of changes]

## Related Issue
Fixes #[issue number]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested manually on real hardware
- [ ] Tested with Home Assistant restart
- [ ] Tested integration reload
- [ ] No errors in logs
- [ ] Checked all affected entities

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] All tests pass
- [ ] No breaking changes (or documented)

## Screenshots
[If applicable]

## Additional Notes
[Any additional information]
```

## 🔍 Code Review

All submissions require review. We review:

- **Code quality**: Clean, maintainable code
- **Functionality**: Works as intended
- **Documentation**: Clear and complete
- **Testing**: Thoroughly tested
- **Breaking changes**: Clearly documented

## 🐛 Debugging Tips

### Enable Debug Logs

```yaml
logger:
  default: info
  logs:
    custom_components.balboa_gs500z: debug
    custom_components.balboa_gs500z.tcp_client: debug
    custom_components.balboa_gs500z.coordinator: debug
```

### Test TCP Connection

```bash
# Test connection to EW11A
telnet 192.168.1.100 8899

# Should see frames:
[643F2B...]
[643F2B...]
```

### Monitor Frames

```bash
# Watch logs in real-time
tail -f home-assistant.log | grep balboa_gs500z
```

### Decode Frames Manually

```python
frame_hex = "643F2B4A004C..."
frame_bytes = bytes.fromhex(frame_hex)

water_temp = round(frame_bytes[3] * 0.5)
setpoint = round(frame_bytes[5] * 0.5)
mode = frame_bytes[23]
heater = frame_bytes[19] & 0x01

print(f"Water: {water_temp}°C, Setpoint: {setpoint}°C, Mode: 0x{mode:02X}, Heater: {heater}")
```

## 📚 Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Home Assistant Architecture](https://developers.home-assistant.io/docs/architecture_index)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [RS-485 Protocol](https://en.wikipedia.org/wiki/RS-485)

## 🤝 Community

- Be respectful and inclusive
- Help others when you can
- Share your knowledge
- Be patient with newcomers

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

If you have questions:
- Check existing issues and discussions
- Ask in the issue tracker
- Be specific and provide context

Thank you for contributing! 🎉
