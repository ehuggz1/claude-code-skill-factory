# Bug Report: NullReferenceException in OrderProcessor.ProcessOrder

**JIRA Issue**: [ECOM-1234](https://your-company.atlassian.net/browse/ECOM-1234)

## Severity
**High** - Feature unavailable or severely degraded

## Environment
- **Language**: C#
- **Component**: Order
- **Class**: OrderProcessor
- **Method**: ProcessOrder
- **File**: `OrderProcessor.cs:45`
- **Namespace**: MyApp.Services.Order
- **Reported**: 2025-11-04 14:30:22

## Description
NullReferenceException: Object reference not set to an instance of an object.

Missing null check before accessing object members. The code attempts to access properties or methods on a potentially null object.

## Steps to Reproduce
1. Call the ProcessOrder method
2. Pass null or uninitialized object as parameter
3. Observe NullReferenceException

## Expected Behavior
The method should handle null inputs gracefully or validate parameters before use.

## Actual Behavior
The code throws `NullReferenceException`: Object reference not set to an instance of an object.

```csharp
NullReferenceException: Object reference not set to an instance of an object.
   at OrderProcessor.ProcessOrder in OrderProcessor.cs:line 45
```

## Root Cause
Missing null check before accessing object members. The code attempts to access properties or methods on a potentially null object.

## Suggested Fix
```csharp
// Add null check before accessing object members
if (obj?.Property != null) {
    // Safe to access
    var value = obj.Property;
}

// Or use null-coalescing operator
var result = obj?.Property ?? defaultValue;
```

## Impact
- Feature unavailable or severely degraded
- Significant user experience impact
- Potential for data inconsistency
- Order component affected

---
**JIRA**: ECOM-1234
**Generated**: 2025-11-04 14:30:22
**Reporter**: Claude (C# Bug Documentation Skill)
