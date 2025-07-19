# winx-user-auth-service
make bet enjoy your life

## Add Role
url: {base_url}/user-auth/api/v1/create_roles
method: POST


Body:

```
{
    "name":"User",
    "abbr":"User"
}
```

## User Login


url: {base_url}/user-auth/api/v1/login

method: POST


Body:

```
{
  "username": "johndoe",
  "password": "securepassword"
}
```

## Create User


url: {base_url}/user-auth/api/v1/create-user

method: POST


Body:

```
{ 
  "name": "John Doe",
  "phone": "1234567890",
  "currency": "USD",
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

## Add Permissions
url: {base_url}/user-auth/api/v1/create_permissions
method: POST


Body:

```
{
    "name":"Wallet",
}
```


## Set Role Permissions
url: {base_url}/user-auth/api/v1/set_role_permissions
method: POST


Body:

```
{
    "role_id": 1,
    "permission_ids": [1, 2]
}
```


## Get User Info


url: {base_url}/user-auth/api/v1/user/userinfo?9

method: GET


## Update User



url: {base_url}/user-auth/api/v1/user/update/9

method: PUT


Body:

```
{
    "name":"ArnabRana",
    "date_of_birth":"20-12-2996",
    "phone":"01681081476",
    "currency":"tk",
    "username":"arnab",
    "email":"ranabiswas02@gmail.com"

}
```

## password reset 

url: {base_url}/user-auth/api/v1/password-reset/9

method: POST


Body:

```
{
  "email": "ranabiswas02@gmail.com",
  "otp": "123456",
  "current_password": "1234",
  "new_password": "12345",
  "confirm_password": "12345"
}
```



## Create wallet


url: {base_url}/user-auth/api/v1/create-wallet

method: POST


Body:

```
{
  "id": 2,
  "user_id": 10,
  "balance": "1000.50",
  "transaction_type": "deposit",
  "amount": "3400.00",
  "previous_balance": "6600.50",
  "status": "pending",
  "reference_id": "txn90329",
  "created_at": "2025-03-19T20:14:50.721604",
  "updated_at": "2025-03-19T20:14:50.721604"
}
```



## Forget Password


url: {base_url}/user-auth/api/v1/forget-password

method: POST


Body:

```
{
"email":"ranabiswas02@email.com"
}