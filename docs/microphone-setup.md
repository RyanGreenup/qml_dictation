# Microphone Setup (Linux/PipeWire)

This guide covers setting the default microphone on Linux systems running PipeWire (standard on Arch, EndeavourOS, Fedora, and most modern distros).

## List Available Microphones

```bash
wpctl status
```

Look under the **Audio > Sources** section:

```
├─ Sources:
│      65. Tiger Lake-LP Smart Sound Technology Audio Controller Stereo Microphone [vol: 1.00]
│      66. Tiger Lake-LP Smart Sound Technology Audio Controller Digital Microphone [vol: 0.27]
│  * 103. Yeti Nano Analog Stereo             [vol: 1.00]
```

The `*` marks the current default. Note the **ID number** (e.g., `103` for Yeti Nano).

## Set Default Microphone

```bash
wpctl set-default <ID>
```

Example - set Yeti Nano as default:
```bash
wpctl set-default 103
```

Example - switch to laptop's built-in mic:
```bash
wpctl set-default 66
```

## Adjust Volume

```bash
wpctl set-volume <ID> <LEVEL>
```

Examples:
```bash
wpctl set-volume 103 1.0      # 100% volume
wpctl set-volume 103 0.8      # 80% volume
wpctl set-volume 103 1.2      # 120% (boost)
```

## GUI Alternative

If you prefer a graphical interface:

```bash
pavucontrol
```

Go to the **Input Devices** tab to select and configure your microphone.

## Verify

After changing, verify with:
```bash
wpctl status | grep -A5 "Sources:"
```

The `*` should now be next to your chosen device.

## Troubleshooting

### Device not showing
- Reconnect USB microphones
- Check `dmesg | tail -20` for connection errors

### No audio captured
- Ensure the device isn't muted: `wpctl set-mute <ID> 0`
- Check volume isn't zero: `wpctl set-volume <ID> 1.0`

### Test recording
```bash
# Record 5 seconds
pw-record --target <ID> test.wav &
sleep 5
kill %1

# Play back
pw-play test.wav
```
