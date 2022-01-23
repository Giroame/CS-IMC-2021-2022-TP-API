# CS-IMC-2021-2022-TP-API

# Resource deployment
## Infra
Through terraform, using api.tf in the azure console.
Type 
```
terraform validate
terraform plan -out main.plan
terraform apply main.plan
```

Destroy resources with :

```
terraform destroy
```

## Code
CI/CD with github action. Secret added with the "secret" option in github.




