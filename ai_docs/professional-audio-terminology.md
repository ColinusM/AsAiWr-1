# Professional Audio Terminology for Voice Control Implementation

> **AI Implementation Context**: This document provides comprehensive professional audio terminology that must be preserved when porting the Python voice command engine to Swift. This terminology represents decades of professional audio engineering conventions and must be implemented with high accuracy and confidence scoring.

## 1. Core Mixing Console Components

### Channel Controls
- **Fader**: Sliding volume control for each audio channel (most common voice command target)
- **Channel Strip**: Complete set of controls for one audio input
- **Gain/Trim**: Input sensitivity adjustment (analog gain staging)
- **Pad**: Reduces input signal by fixed amount (usually 10-20dB)
- **Phantom Power**: +48V power for condenser microphones
- **High-Pass Filter (HPF)**: Removes low frequencies below set point
- **EQ**: Frequency adjustment controls (High, High-Mid, Low-Mid, Low)
- **Aux Send**: Secondary outputs for monitor mixes or effects
- **Pan**: Stereo positioning control (left-center-right)
- **Mute**: Silences channel completely
- **Solo**: Isolates channel for monitoring (Pre-Fader Listen or After-Fader Listen)

### Group Controls
- **DCA (Digitally Controlled Amplifier)**: Master control for multiple channels
- **VCA (Voltage Controlled Amplifier)**: Analog equivalent of DCA
- **Group/Bus**: Collection of channels routed together
- **Matrix**: Advanced routing system for complex mixes
- **Mix Bus**: Main stereo output mixing bus
- **Monitor Mix**: Separate mix for performers or engineers

### Scene Management
- **Scene/Snapshot**: Complete mixer state configuration
- **Bank**: Collection of scenes
- **Recall**: Load a previously saved scene
- **Store**: Save current mixer state as scene
- **Library**: Collection of saved settings (scenes, effects, etc.)

## 2. Professional Audio Terminology Database

### Level Control Terms
```
Unity: 0dB (reference level)
Hot: +3 to +5dB (pushed level for prominence)
Cooking: +3 to +5dB (same as hot)
Quiet: -10dB (subdued level)
Bury: -15dB (very low in mix)
Inaudible: -30dB or muted
Nominal: Standard operating level (usually 0dB)
Headroom: Available level above nominal before clipping
```

### Professional Slang Terms
```
Crank: Increase level significantly
Slam: Push level hard (aggressive increase)
Smash: Maximum level increase
Push: Moderate level increase
Pull/Bring Up: Increase level
Pull Down: Decrease level
Ride: Continuously adjust level during performance
Park: Set and leave at specific level
```

### Instrument Common Names
```
Vocals: Lead vocals, backing vocals, harmony vocals
Vox: Informal term for vocals
Kick: Kick drum, bass drum
BD: Bass drum (abbreviated)
Snare: Snare drum
Hat: Hi-hat cymbals
Ride: Ride cymbal
Crash: Crash cymbal
Toms: Tom-tom drums
OH: Overhead microphones (drum overheads)
Room: Room microphones for ambience
Bass: Bass guitar
Guitar: Electric guitar
Acoustic: Acoustic guitar
Keys: Keyboard, piano, synthesizer
Strings: String section or synthesized strings
Brass: Horn section
Woodwinds: Saxophone, clarinet, flute section
```

### Frequency Range Terms
```
Sub: Below 60Hz (sub-bass)
Low/Bass: 60Hz-250Hz
Low-Mid: 250Hz-500Hz
Mid/Midrange: 500Hz-2kHz
High-Mid/Presence: 2kHz-5kHz
High/Treble: 5kHz-10kHz
Air: 10kHz and above
Fundamental: Primary frequency of note
Harmonics: Overtones above fundamental
Muddiness: Excessive low-mid frequencies
Boxiness: Excessive midrange resonance
Harshness: Excessive high-mid frequencies
Sibilance: Excessive 6-8kHz on vocals
```

## 3. Voice Command Pattern Categories

### Level Adjustment Commands
```
Direct Level:
- "Set channel 1 to unity"
- "Bring channel 3 to minus 6"
- "Channel 5 at plus 3 dB"

Relative Level:
- "Bring up the vocals"
- "Pull down channel 2"
- "Push the kick up 3 dB"

Professional Slang:
- "Crank channel 4"
- "Bury the guitar"
- "Make the vocals hot"
- "Keep the bass cooking"
```

### Mute/Solo Commands
```
Mute:
- "Mute channel 8"
- "Kill the drums"
- "Turn off channel 3"
- "Silence the piano"

Unmute:
- "Unmute channel 8"
- "Restore the drums"
- "Turn on channel 3"
- "Bring back the piano"

Solo:
- "Solo channel 5"
- "PFL channel 2"
- "Listen to the bass"
- "Clear all solos"
```

### Routing Commands
```
Aux Sends:
- "Send vocals to monitor 1"
- "Add channel 3 to mix 2"
- "Route drums to aux 4"
- "Feed the guitar to wedges"

Pan Commands:
- "Pan vocals center"
- "Put guitar hard left"
- "Spread the drums wide"
- "Center the bass"
```

### EQ Commands
```
Frequency Adjustment:
- "Add high-end to vocals"
- "Cut the low-mids on guitar"
- "Boost the presence on snare"
- "Roll off the bass below 80"

High-Pass Filter:
- "High-pass the vocals"
- "HPF channel 4 at 100"
- "Roll off the low end"
```

### Scene Management
```
Scene Recall:
- "Load scene 3"
- "Recall soundcheck"
- "Go to scene bank 2"
- "Switch to scene 15"

Scene Storage:
- "Save current scene"
- "Store as scene 5"
- "Update soundcheck scene"
```

## 4. RCP Command Mapping

### Channel Commands
```
Fader Level:
Voice: "Set channel 1 to minus 6 dB"
RCP: set MIXER:Current/InCh/Fader/Level 0 0 -600

Channel Mute:
Voice: "Mute channel 3"
RCP: set MIXER:Current/InCh/Fader/On 2 0 0

Channel Solo:
Voice: "Solo channel 5"  
RCP: set MIXER:Current/InCh/ToMix/On 4 0 1
```

### DCA Commands
```
DCA Level:
Voice: "Set DCA 1 to unity"
RCP: set MIXER:Current/DCA/Fader/Level 0 0 0

DCA Mute:
Voice: "Mute DCA 2"
RCP: set MIXER:Current/DCA/Fader/On 1 0 0
```

### Scene Commands
```
Scene Recall:
Voice: "Recall scene 15"
RCP: ssrecall_ex scene_15

Scene Store:
Voice: "Store scene 10"
RCP: ssstore scene_10
```

## 5. Confidence Scoring Guidelines

### High Confidence (0.9-1.0)
- Exact channel numbers with specific dB values
- Standard terminology (mute, solo, unity, etc.)
- Professional commands with clear intent

### Medium Confidence (0.7-0.9)
- Professional slang terms (crank, bury, hot)
- Instrument names with implied channel assignments
- Relative level adjustments

### Low Confidence (0.5-0.7)
- Ambiguous references ("it", "that channel")
- Non-standard terminology
- Complex compound commands requiring interpretation

### Reject (<0.5)
- Unclear or potentially harmful commands
- Invalid channel/DCA numbers
- Nonsensical audio terminology

## 6. Error Handling and Validation

### Input Validation
```
Channel Range: 1-40 (varies by mixer model)
DCA Range: 1-8
Scene Range: 1-100
dB Range: -60dB to +10dB
String Length: Maximum 200 characters
```

### Security Considerations
- Never log sensitive RCP commands to prevent eavesdropping
- Validate all numeric inputs to prevent injection
- Rate limit commands to prevent mixer overload
- Implement command whitelisting for safety

## 7. Implementation Notes for Swift Port

### Data Structures
- Use enums for command categories and actions
- Implement confidence scoring as Double (0.0-1.0)
- Use structured data for professional terminology lookup
- Implement caching for compiled regex patterns

### Performance Optimizations
- Pre-compile all regex patterns at initialization
- Use Dictionary for fast instrument name lookups
- Implement LRU cache for common command patterns
- Batch similar commands for efficiency

### Professional Audio Context
- Preserve exact terminology from decades of industry standards
- Maintain compatibility with existing RCP command structure
- Support both formal and slang terminology equally
- Implement context-aware command interpretation

This terminology database represents the foundation for accurate voice command interpretation in professional audio environments. The Swift implementation must preserve the nuanced understanding of how audio engineers actually communicate with mixing consoles.

## External References

- **iZotope Audio Glossary**: https://www.izotope.com/en/learn/a-glossary-of-common-and-confusing-mixing-terms.html
- **Sound on Sound Glossary**: https://www.soundonsound.com/glossary
- **Yamaha RCP Documentation**: `/docs/yamaha-rcp/official-docs/yamaha-rcp-docs/README.md`
- **Professional Audio Terms**: https://www.masteringbox.com/learn/audio-mixing-mastering-terms