def main():
    response = requests.get(f'{base_url}/users/AveryClapp/repos', headers=headers)
    print(response.json())


if __name__ == "__main__":
    main()
