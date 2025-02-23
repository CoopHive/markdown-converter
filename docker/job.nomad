job "my-job-2" {
  datacenters = ["dc1"]
  type        = "batch"

  group "my-group" {
    task "my-task" {
      driver = "docker"

      resources {
        memory = 1024 # Increased memory for handling larger files
        cpu    = 500  # Adjust CPU resources if needed
      }

      config {
        image = "vardhan03/chunk:latest"
        args  = ["paragraph", "https://gateway.lighthouse.storage/ipfs/bafkreicsfswmd5zrvb6bzb4ayqfv546kakiyipzpzkqxrjmvx264lwyzk4"]
      }
    }
  }
}
