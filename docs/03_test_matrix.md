# Test Matrix — Invoice Dataset

## Categories

### Clean (10)
- Full data
- High quality
- Expected: Approved

### Noisy (8)
- Image quality issues
- Rotated / blurred
- Expected: Needs review

### Missing Fields (6)
- Missing invoice ID / total / date
- Expected: Needs review

### Duplicates (3)
- Same invoice ID + vendor + amount
- Expected: Suspected duplicate

### Suspicious (5)
- Invalid dates
- Unknown vendor
- Extreme amounts
- Expected: Needs review or fraud