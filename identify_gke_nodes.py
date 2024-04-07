"""
Retrieves total number of nodes used by GKE COS and GKE Autopilot clusters using gcloud command.
Requires gcloud CLI to be installed and configured.
"""

import subprocess
import json


def get_all_gcp_projects():
  """
  Executes a gcloud command to list all project IDs and returns them as a list.
  """
  projects = []

  command = 'gcloud projects list --format="json(projectId)"'
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  output, err = process.communicate()

  if err:
    raise RuntimeError(f"Error running gcloud command: {err.decode()}")
  raw_data = json.loads(output.decode())

  for data in raw_data:
    projects.append(data['projectId'])

  return projects


def main():
  try:
    total_standard_nodes = 0
    total_autopilot_nodes = 0

    projects = get_all_gcp_projects()

    print(f"Found {len(projects)} GCP projects\n")

    for project in projects:
      try:
        print(f'###### Project Name: {project} #########\n')

        command = f'gcloud container clusters list --project {project} --format="json()"'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        output, err = process.communicate()

        output = json.loads(output)

        if len(output) < 1:
          print(f'Project {project} has no GKE clusters. Skipping.\n')
          continue

        for x in output:
          print(f'Cluster Name: {x["name"]}')

          if 'autopilot' in x and 'enabled' in x['autopilot']:
            print(x['name'], 'is a GKE Autopilot cluster')

            if 'currentNodeCount' in x:
              total_autopilot_nodes += int(x['currentNodeCount'])
              print(f'Current Node Count {x["currentNodeCount"]}\n')
            else:
              print(f'Cluster {x["name"]} has no nodes\n')
          else:
            print(x['name'], 'is a GKE Standard cluster')

            if 'currentNodeCount' in x:
              total_standard_nodes += int(x['currentNodeCount'])
              print(f'Current Node Count {x["currentNodeCount"]}\n')
            else:
              print(f'Cluster {x["name"]} has 0 nodes\n')
      except subprocess.CalledProcessError as err:
        print(f"Error processing cluster information for project {project}: {err.output}\n")
      except json.decoder.JSONDecodeError as err:
        print(f'Kubernetes Engine API has not been used in project {project}\n')
      except Exception as err:
        print(f'Generic error: {err}\n')

    print('##########################\n')
    print(f'Total GKE Standard Nodes: {total_standard_nodes}')
    print(f'Total GKE Autopilot Nodes: {total_autopilot_nodes}')
  except RuntimeError as err:
    print(f"An error occurred: {err}")


if __name__ == '__main__':
  main()
