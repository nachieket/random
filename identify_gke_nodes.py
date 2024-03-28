"""
Retrieves total number of nodes used by GKE COS and GKE Autopilot clusters using gcloud command.
Requires gcloud CLI to be installed and configured.
"""

import subprocess
import re


def get_all_gcp_projects():
  """
  Executes a gcloud command to list all project IDs and returns them as a list.
  """
  command = 'gcloud projects list --format="text(projectId)"'
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  output, err = process.communicate()
  if err:
    raise RuntimeError(f"Error running gcloud command: {err.decode()}")
  return output.decode().splitlines()


def main():
  try:
    projects = get_all_gcp_projects()
    print(f"Found {len(projects)} GCP projects\n")
    names = []
    total_cos_nodes = 0
    total_autopilot_nodes = 0

    for project in projects:
      if "project_id" in project:
        names.append(project.split(' ')[1])

    for name in names:
      try:
        command = f'gcloud container clusters list --project {name}'
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        output, err = process.communicate()
        clusters = output.split('\n\n')

        if output:
          pattern = r"(NAME|LOCATION|NUM_NODES): (.*)"

          for x in clusters:
            results = {}
            for match in re.finditer(pattern, x, flags=re.MULTILINE):
              key = match.group(1).lower()  # Convert key to lowercase for consistency
              value = match.group(2).strip()  # Remove leading/trailing whitespace
              results[key] = value

            try:
              command = f'gcloud container node-pools list --cluster {results["name"]} --project {name} --format="value(name)" --region {results["location"]}'
              process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
              output, err = process.communicate()

              if output:
                if results["num_nodes"]:
                  print(f'GKE COS cluster {results["name"]} in project {name} has {results["num_nodes"]} node/s')
                  total_cos_nodes += int(results["num_nodes"])
                else:
                  print(f'GKE COS cluster {results["name"]} in project {name} has no node/s')
              elif err:
                if results["num_nodes"]:
                  print(f'GKE Autopilot cluster {results["name"]} in project {name} has {results["num_nodes"]} node/s')
                  total_autopilot_nodes += int(results["num_nodes"])
                else:
                  print(f'GKE Autopilot cluster {results["name"]} in project {name} has no node/s')
            except subprocess.CalledProcessError as e:
              print(f'Error: {e}')
      except subprocess.CalledProcessError as err:
        print(f"Error processing cluster information for project {name}: {err.output}")

    print(f'\n\nTotal GKE COS nodes are {total_cos_nodes}')
    print(f'Total GKE Autopilot nodes are {total_autopilot_nodes}')
  except RuntimeError as err:
    print(f"An error occurred: {err}")


if __name__ == '__main__':
  main()
