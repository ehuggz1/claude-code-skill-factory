"""
C# Bug Analyzer

Analyzes C# code, exceptions, and stacktraces to extract bug information.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class BugAnalyzer:
    """Analyzes C# bugs and exceptions"""

    # Common C# exceptions and their severity
    EXCEPTION_SEVERITY = {
        'NullReferenceException': 'High',
        'OutOfMemoryException': 'Critical',
        'StackOverflowException': 'Critical',
        'InvalidOperationException': 'High',
        'ArgumentNullException': 'High',
        'ArgumentException': 'Medium',
        'IndexOutOfRangeException': 'High',
        'DivideByZeroException': 'High',
        'FileNotFoundException': 'Medium',
        'IOException': 'Medium',
        'UnauthorizedAccessException': 'High',
        'TimeoutException': 'Medium',
        'SqlException': 'Critical',
        'DbUpdateException': 'Critical',
    }

    def __init__(self):
        self.exception_pattern = re.compile(
            r'(?:System\.)?(\w+(?:Exception|Error)): (.+)',
            re.MULTILINE
        )
        self.stacktrace_pattern = re.compile(
            r'at (.+?) in (.+?):line (\d+)',
            re.MULTILINE
        )
        self.simple_location_pattern = re.compile(
            r'at (.+?)\.(\w+)\(.*?\)',
            re.MULTILINE
        )

    def analyze(
        self,
        code: Optional[str] = None,
        stacktrace: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Analyze bug information and return structured data.

        Args:
            code: C# code snippet (optional)
            stacktrace: Exception stacktrace (optional)
            description: User-provided bug description (optional)

        Returns:
            Dict with keys: exception_type, message, severity, file_path,
            line_number, method, class_name, root_cause, component
        """
        result = {
            'exception_type': None,
            'message': None,
            'severity': 'Medium',  # default
            'file_path': None,
            'line_number': None,
            'method': None,
            'class_name': None,
            'namespace': None,
            'root_cause': None,
            'component': None,
            'timestamp': datetime.now().isoformat(),
        }

        # Extract exception info from stacktrace
        if stacktrace:
            result.update(self._parse_stacktrace(stacktrace))

        # Analyze code if provided
        if code:
            result.update(self._analyze_code(code, result))

        # Use description if provided
        if description:
            result['user_description'] = description

        # Determine severity based on exception type
        if result['exception_type']:
            result['severity'] = self.EXCEPTION_SEVERITY.get(
                result['exception_type'],
                'Medium'
            )

        # Extract component from namespace or file path
        result['component'] = self._determine_component(result)

        return result

    def _parse_stacktrace(self, stacktrace: str) -> Dict:
        """Parse C# stacktrace to extract exception and location info"""
        result = {}

        # Find exception type and message
        exception_match = self.exception_pattern.search(stacktrace)
        if exception_match:
            result['exception_type'] = exception_match.group(1)
            result['message'] = exception_match.group(2).strip()

        # Find file location with line number
        location_match = self.stacktrace_pattern.search(stacktrace)
        if location_match:
            full_method = location_match.group(1)
            result['file_path'] = location_match.group(2)
            result['line_number'] = int(location_match.group(3))

            # Parse method and class from full method path
            parts = full_method.rsplit('.', 1)
            if len(parts) == 2:
                result['class_name'] = parts[0].split('.')[-1]
                result['namespace'] = parts[0].rsplit('.', 1)[0] if '.' in parts[0] else None
                result['method'] = parts[1].split('(')[0]
        else:
            # Try simpler pattern without file path
            simple_match = self.simple_location_pattern.search(stacktrace)
            if simple_match:
                full_path = simple_match.group(1)
                result['method'] = simple_match.group(2)

                parts = full_path.split('.')
                if len(parts) >= 2:
                    result['class_name'] = parts[-1]
                    result['namespace'] = '.'.join(parts[:-1])

        return result

    def _analyze_code(self, code: str, existing_data: Dict) -> Dict:
        """Analyze C# code to identify potential issues"""
        result = {}

        # Identify common bug patterns
        if existing_data.get('exception_type') == 'NullReferenceException':
            if self._has_null_dereference(code):
                result['root_cause'] = (
                    "Missing null check before accessing object members. "
                    "The code attempts to access properties or methods on a potentially null object."
                )

        elif existing_data.get('exception_type') == 'InvalidOperationException':
            if 'foreach' in code.lower() or 'enumerator' in existing_data.get('message', '').lower():
                result['root_cause'] = (
                    "Collection was modified during enumeration. "
                    "The code is adding or removing items from a collection while iterating over it."
                )

        elif existing_data.get('exception_type') == 'DivideByZeroException':
            if '/' in code:
                result['root_cause'] = (
                    "Division by zero. "
                    "The code performs division without checking if the divisor is zero."
                )

        elif existing_data.get('exception_type') == 'IndexOutOfRangeException':
            if '[' in code and ']' in code:
                result['root_cause'] = (
                    "Array or list index out of bounds. "
                    "The code accesses an index that doesn't exist in the collection."
                )

        # Extract class name from code if not already found
        if not existing_data.get('class_name'):
            class_match = re.search(r'class\s+(\w+)', code)
            if class_match:
                result['class_name'] = class_match.group(1)

        # Extract method name from code if not already found
        if not existing_data.get('method'):
            method_match = re.search(
                r'(?:public|private|protected|internal)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',
                code
            )
            if method_match:
                result['method'] = method_match.group(1)

        return result

    def _has_null_dereference(self, code: str) -> bool:
        """Check if code has potential null dereference"""
        # Look for property/method access without null checks
        patterns = [
            r'\w+\.\w+',  # object.property or object.method()
            r'\w+\[\d+\]',  # array[index]
        ]

        for pattern in patterns:
            if re.search(pattern, code):
                # Check if there's a null check nearby
                if '== null' not in code and '!= null' not in code and '?.' not in code:
                    return True

        return False

    def _determine_component(self, data: Dict) -> Optional[str]:
        """Determine JIRA component from namespace or file path"""
        namespace = data.get('namespace')
        file_path = data.get('file_path')

        if namespace:
            # Extract component from namespace
            # e.g., "MyApp.Services.Payment" -> "Payment"
            parts = namespace.split('.')
            if len(parts) >= 2:
                return parts[-1] if parts[-1] not in ['Services', 'Controllers', 'Models'] else parts[-2]
            return parts[0]

        if file_path:
            # Extract component from file path
            # e.g., "Services/Payment/PaymentService.cs" -> "Payment"
            path_parts = file_path.replace('\\', '/').split('/')
            if len(path_parts) >= 2:
                return path_parts[-2]

        return None

    def generate_reproduction_steps(
        self,
        exception_type: str,
        method: Optional[str] = None,
        code: Optional[str] = None
    ) -> List[str]:
        """Generate steps to reproduce the bug"""
        steps = []

        if method:
            steps.append(f"Call the {method} method")
        else:
            steps.append("Execute the affected code")

        # Add exception-specific steps
        if exception_type == 'NullReferenceException':
            steps.append("Pass null or uninitialized object as parameter")
            steps.append("Observe NullReferenceException")
        elif exception_type == 'InvalidOperationException':
            steps.append("Modify the collection during iteration")
            steps.append("Observe InvalidOperationException")
        elif exception_type == 'DivideByZeroException':
            steps.append("Provide zero as divisor")
            steps.append("Observe DivideByZeroException")
        else:
            steps.append(f"Observe {exception_type}")

        return steps

    def suggest_fix(
        self,
        exception_type: str,
        code: Optional[str] = None
    ) -> Optional[str]:
        """Suggest code fix based on exception type"""
        if exception_type == 'NullReferenceException':
            return """// Add null check before accessing object members
if (obj?.Property != null) {
    // Safe to access
    var value = obj.Property;
}

// Or use null-coalescing operator
var result = obj?.Property ?? defaultValue;"""

        elif exception_type == 'InvalidOperationException':
            return """// Option 1: Create a copy before iterating
foreach (var item in collection.ToList()) {
    ProcessItem(item);
}

// Option 2: Use for loop in reverse
for (int i = collection.Count - 1; i >= 0; i--) {
    ProcessItem(collection[i]);
}"""

        elif exception_type == 'DivideByZeroException':
            return """// Check for zero before division
if (divisor != 0) {
    var result = numerator / divisor;
} else {
    // Handle zero case
    var result = 0; // or throw exception, or return error
}"""

        elif exception_type == 'IndexOutOfRangeException':
            return """// Check bounds before accessing
if (index >= 0 && index < array.Length) {
    var value = array[index];
} else {
    // Handle out of bounds
}"""

        return None

    def determine_impact(
        self,
        severity: str,
        component: Optional[str] = None
    ) -> List[str]:
        """Determine business/technical impact of the bug"""
        impacts = []

        if severity == 'Critical':
            impacts.append("Application crash or complete service disruption")
            impacts.append("Potential data loss or corruption")
            impacts.append("Immediate user impact")
        elif severity == 'High':
            impacts.append("Feature unavailable or severely degraded")
            impacts.append("Significant user experience impact")
            impacts.append("Potential for data inconsistency")
        elif severity == 'Medium':
            impacts.append("Reduced functionality")
            impacts.append("User workaround available")
        else:  # Low
            impacts.append("Minor inconvenience")
            impacts.append("Cosmetic or edge case issue")

        if component:
            impacts.append(f"{component} component affected")

        return impacts


def analyze_bug(
    code: Optional[str] = None,
    stacktrace: Optional[str] = None,
    description: Optional[str] = None
) -> Dict:
    """
    Convenience function to analyze a bug.

    Usage:
        result = analyze_bug(stacktrace="System.NullReferenceException...")
    """
    analyzer = BugAnalyzer()
    return analyzer.analyze(code=code, stacktrace=stacktrace, description=description)


if __name__ == '__main__':
    # Example usage
    sample_stacktrace = """
System.NullReferenceException: Object reference not set to an instance of an object.
   at OrderProcessor.ProcessOrder(Order order) in OrderProcessor.cs:line 45
   at OrderController.SubmitOrder() in OrderController.cs:line 23
"""

    result = analyze_bug(stacktrace=sample_stacktrace)

    print("Bug Analysis Results:")
    print(f"Exception: {result['exception_type']}")
    print(f"Message: {result['message']}")
    print(f"Severity: {result['severity']}")
    print(f"File: {result['file_path']}:{result['line_number']}")
    print(f"Method: {result['class_name']}.{result['method']}")
    print(f"Component: {result['component']}")
