# Halloumi Cloudwatch Dashboard

Create a dashboard in the AWS Cloudwatch using the best practices from Halloumi.

## Install

From pip:

```bash
pip install halloumi-cloudwatch-dashboard
```

From npm:

```bash
npm install halloumi-cloudwatch-dashboard
```

## API Documentation

Check [API Documentation](./API.md)

## Usage

### Python

```python
from aws_cdk import core
from halloumi-cloudwatch-dashboard import Dashboard

app = core.App()

stack = core.Stack(app, 'MainStack')
...

Dashboard(
    stack,
    'Dashboard',
    dashboardName='MyDashboard'
)
```

### Typescript

```typescript
import * as cdk from '@aws-cdk/core';
import { Dashboard } from '@halloumi-cloudwatch-dashboard';

export class CdkWorkshopStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    Dashboard(this, 'Dashboard', dashboardName='MyDashboard');
  }
}
```
