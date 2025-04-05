# How Use?
## Open Terminal Linux and
cd /home/$USER
git clone git@github.com:RestlessByte/taskForSpacesProjects.git 
cd taskForSpacesProjectsR
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
 uvicorn tests:app --reload
curl -X POST "http://localhost:8000/match" \
-H "Content-Type: application/json" \
-d '{"skills": ["VR Design", "AI"], "interests": ["Tech Innovation"]}'