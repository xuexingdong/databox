import requests

if __name__ == '__main__':
    count = 0
    with open('qrcode_pics.txt') as f:
        for line in f:
            line = line.strip()
            content = requests.get(line).content
            count += 1
            with open('../imgs/' + str(count) + '.jpg', 'wb') as fout:
                fout.write(content)
