docker build . -t cyberhack2021pw4/kali:latest
docker kill cyberhack2021pw4_kali || true
#docker run --rm -d --name cyberhack2021pw4_kali cyberhack2021pw4/kali
docker run --rm --name cyberhack2021pw4_kali -d -e test=pippozzo -e NUOVA_PASSWORD=Pippozzo33 -e SSH_PUB_USER="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC87JS8Uz4Co811tTj8xb2aAhMJOLnsUOaYcuw93dgQjaN6eS3iDH6ksg4fEx0Xn3VrIVB9B97dlxpHPlgEKxJiUeyRuADEKnAaO9444lKXVb0sBmor1Dj1FWU3Q59k9rgEj9gkoNAhqnoVzRDKMAb4opv3vleySgwFDrf6f162wS5HT9ASS1WLs6CeXV64TkE+6OtAUmEUKySiU/Y2vA5ojCVfJUTEowyK+tMDp79+CvZLIwdukUaw/qFTehP18mqhySSrhxnDF+qVB5MstxRew/V5tRyoAO+1NrPZO/2D1r4FyAew55Pmbvt4xLhe4zgh8xHIN8gNn0T6K0jFXcll Roberto@jarvis.fritz.box" -it -p 2222:22 cyberhack2021pw4/kali:v4
docker exec cyberhack2021pw4_kali ifconfig eth0 | grep inet
