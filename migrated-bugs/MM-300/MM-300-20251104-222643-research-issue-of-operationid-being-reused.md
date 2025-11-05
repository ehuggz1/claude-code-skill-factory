# [BUG] Research Issue of OperationID Being Reused

**Source**: Migrated from JIRA [MM-300](https://api.atlassian.com/ex/jira/8370cbc7-fe4d-41d3-acce-026ca01f3323/browse/MM-300)

## Description

Adding in the previously documented good telemetry from Patricia's initial email:  
**Sent:** Tuesday, October 28, 2025 9:10 AM  
**Subject:** Callbacks Under One OperationID  
  
We found when researching a TST callback issue, that OperationID's were getting reused again. 

OperationID - 13d7a73cad0859013f68e6ecefe0ef44 is returning the following:

  If I look at <Customer> callback failures from Sunday the telemetry looks like the following:

But when I look at one from this morning it looks like the following.  Its mixed in with other successful callbacks instead of having it's own telemetry. And I'm not getting the same kind of information.

## Steps to Reproduce

1. Deploy Azure Function to isolated mode (.NET 8)
2. Trigger multiple TST callback operations
3. Monitor Application Insights telemetry
4. Search for OperationID: `13d7a73cad0859013f68e6ecefe0ef44`
5. Observe multiple distinct operations sharing the same OperationID

## Expected Behavior

Each callback operation should have:
- **Unique OperationID** for proper distributed tracing
- Isolated telemetry trace (not mixed with other operations)
- Complete operation details (start, end, dependencies)
- Clear success/failure status per operation

## Actual Behavior

Multiple callback operations share the same OperationID, causing:
- **Telemetry Corruption**: Successful and failed callbacks mixed together
- **Information Loss**: Cannot get detailed information for individual callbacks
- **Debugging Impossibility**: Cannot isolate specific callback failures
- **Production Impact**: Unable to effectively monitor and troubleshoot production issues

## Environment

- **Framework**: .NET 8.0
- **Azure Functions Mode**: Isolated Worker Process (bug occurs) vs In-Process (bug does not occur)
- **Azure Functions Runtime**: [Need to verify version]
- **Application Insights**: P-RREZ-V10-AI
- **Subscription**: ba3bdab0-9c6d-4336-9bba-e938d5bd34cf
- **Resource Group**: P-RREZ-V10-CORE-01RG
- **Environment**: Production
- **Issue Type**: Intermittent (happens periodically)

## Severity

**Critical** - Production rollback trigger

**Impact**:
- Cannot effectively monitor production callback operations
- Unable to debug callback failures in isolated mode
- Blocks migration to Azure Functions isolated mode
- Affects production observability and incident response

## Workaround

**Temporary**: Restart the Azure Function app to clear the OperationID reuse
- This is only a temporary fix
- Issue recurs after some time
- Not a sustainable production solution

**Long-term**: Rolled back to in-process model (non-isolated)
- Previous .NET 8 version without isolated mode
- Issue does not occur in in-process model
- Blocks adoption of isolated mode benefits

## Research Questions

1. **Root Cause**: Why does isolated mode cause OperationID reuse?
2. **Telemetry Initialization**: What changed between in-process and isolated mode?
3. **Activity Context**: Is DistributedContext/Activity being properly propagated?
4. **Azure Functions Runtime**: Is this a known issue in the isolated worker model?
5. **Microsoft Guidance**: Are there documented best practices for telemetry in isolated mode?
6. **Reproducibility**: Can this be reproduced in non-production environments?
