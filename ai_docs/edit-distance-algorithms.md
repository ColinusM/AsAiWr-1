# Edit Distance Algorithms for Voice Command Similarity

## Overview

This document provides implementation details for edit distance algorithms optimized for voice command similarity detection in the iOS Voice Control app.

## Levenshtein Distance Implementation

### Basic Algorithm

The Levenshtein distance calculates the minimum number of single-character edits (insertions, deletions, or substitutions) required to change one string into another.

### Optimized Swift Implementation

```swift
/// Calculates edit distance between two voice commands at the word level
/// Optimized for real-time performance (<100ms)
func calculateEditDistance(_ command1: String, _ command2: String) -> Int {
    // Tokenize by words instead of characters for voice commands
    let words1 = command1.lowercased()
        .components(separatedBy: .whitespaces)
        .filter { !$0.isEmpty }
    
    let words2 = command2.lowercased()
        .components(separatedBy: .whitespaces)
        .filter { !$0.isEmpty }
    
    // Early exit optimization
    let wordCountDiff = abs(words1.count - words2.count)
    if wordCountDiff > 2 {
        return Int.max // Too different to be similar
    }
    
    // Handle empty cases
    if words1.isEmpty { return words2.count }
    if words2.isEmpty { return words1.count }
    
    // Initialize DP table
    var dp = Array(repeating: Array(repeating: 0, count: words2.count + 1), 
                   count: words1.count + 1)
    
    // Base cases
    for i in 0...words1.count {
        dp[i][0] = i
    }
    for j in 0...words2.count {
        dp[0][j] = j
    }
    
    // Fill DP table
    for i in 1...words1.count {
        for j in 1...words2.count {
            if words1[i-1] == words2[j-1] {
                dp[i][j] = dp[i-1][j-1]
            } else {
                dp[i][j] = 1 + min(
                    dp[i-1][j],     // deletion
                    dp[i][j-1],     // insertion
                    dp[i-1][j-1]    // substitution
                )
            }
        }
    }
    
    return dp[words1.count][words2.count]
}
```

### Voice Command Specific Optimizations

1. **Word-Level Comparison**: Instead of character-by-character, we compare word-by-word since voice commands are word-based.

2. **Common Variations Handling**:
```swift
extension String {
    /// Normalize common voice transcription variations
    func normalizedForVoiceComparison() -> String {
        return self
            .replacingOccurrences(of: "minus", with: "-")
            .replacingOccurrences(of: "negative", with: "-")
            .replacingOccurrences(of: "plus", with: "+")
            .replacingOccurrences(of: "positive", with: "+")
            .replacingOccurrences(of: " db", with: " dB")
            .replacingOccurrences(of: " decibels", with: " dB")
            .replacingOccurrences(of: "channel ", with: "ch ")
    }
}
```

3. **Threshold Calculation**:
```swift
func getSimilarityThreshold(for wordCount: Int) -> Int {
    switch wordCount {
    case 0...3:
        return 1  // Very short commands: allow 1 word difference
    case 4...6:
        return 1  // Medium commands: n-1 rule
    default:
        return 2  // Long commands: n-2 rule
    }
}
```

## Performance Considerations

### Time Complexity
- Standard Levenshtein: O(m × n) where m and n are string lengths
- Word-level variant: O(w1 × w2) where w1 and w2 are word counts
- Typical voice command: 3-10 words, so max ~100 operations

### Space Complexity
- O(w1 × w2) for the DP table
- Can be optimized to O(min(w1, w2)) using rolling array technique

### Real-time Optimization

```swift
/// Optimized version using only two rows instead of full matrix
func calculateEditDistanceOptimized(_ command1: String, _ command2: String) -> Int {
    let words1 = command1.lowercased().split(separator: " ")
    let words2 = command2.lowercased().split(separator: " ")
    
    // Always iterate over the shorter array
    let (shorter, longer) = words1.count <= words2.count ? (words1, words2) : (words2, words1)
    
    var previousRow = Array(0...longer.count)
    var currentRow = Array(repeating: 0, count: longer.count + 1)
    
    for (i, word1) in shorter.enumerated() {
        currentRow[0] = i + 1
        
        for (j, word2) in longer.enumerated() {
            if word1 == word2 {
                currentRow[j + 1] = previousRow[j]
            } else {
                currentRow[j + 1] = 1 + min(
                    previousRow[j],      // substitution
                    previousRow[j + 1],  // deletion
                    currentRow[j]        // insertion
                )
            }
        }
        
        swap(&previousRow, &currentRow)
    }
    
    return previousRow[longer.count]
}
```

## Usage in Voice Command Context

### Similarity Check Function

```swift
func areSimilarCommands(_ cmd1: ProcessedVoiceCommand, 
                       _ cmd2: ProcessedVoiceCommand,
                       timeWindow: TimeInterval = 10.0) -> Bool {
    // Check time proximity
    let timeDiff = abs(cmd1.timestamp.timeIntervalSince(cmd2.timestamp))
    guard timeDiff <= timeWindow else { return false }
    
    // Normalize commands
    let normalized1 = cmd1.originalText.normalizedForVoiceComparison()
    let normalized2 = cmd2.originalText.normalizedForVoiceComparison()
    
    // Calculate word count and threshold
    let wordCount = normalized1.split(separator: " ").count
    let threshold = getSimilarityThreshold(for: wordCount)
    
    // Calculate distance
    let distance = calculateEditDistanceOptimized(normalized1, normalized2)
    
    return distance <= threshold
}
```

### Common Voice Command Patterns

These patterns should be considered similar:
- "set channel 1 to -6 dB" ↔ "set channel one to minus six decibels"
- "mute the kick drum" ↔ "mute kick drum"
- "recall scene 3" ↔ "load scene three"

## Testing Considerations

```swift
func testSimilarityDetection() {
    let testCases = [
        // Should be similar (distance ≤ threshold)
        ("set channel 1 to -6", "set channel one to -6", true),
        ("mute kick drum", "mute the kick drum", true),
        ("pan guitar left", "pan the guitar left", true),
        
        // Should NOT be similar (distance > threshold)
        ("set channel 1 to -6", "mute channel 1", false),
        ("recall scene 1", "save scene 1", false),
        ("pan left", "pan right", false)
    ]
    
    for (cmd1, cmd2, expected) in testCases {
        let distance = calculateEditDistance(cmd1, cmd2)
        let wordCount = cmd1.split(separator: " ").count
        let threshold = getSimilarityThreshold(for: wordCount)
        let similar = distance <= threshold
        
        assert(similar == expected, 
               "Failed: '\(cmd1)' vs '\(cmd2)' - distance: \(distance), threshold: \(threshold)")
    }
}
```

## References

1. [Levenshtein Distance - Wikipedia](https://en.wikipedia.org/wiki/Levenshtein_distance)
2. [Dynamic Programming Optimization Techniques](https://www.geeksforgeeks.org/edit-distance-dp-5/)
3. [Swift String Performance Best Practices](https://developer.apple.com/documentation/swift/string)