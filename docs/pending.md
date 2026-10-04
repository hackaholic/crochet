# Pending decisions

These decisions need an answer before related implementation work begins.

| Area | Decision needed | Why it matters | Owner |
| --- | --- | --- | --- |
| Catalogue | Confirm real products, prices, options, images, and stock | Product data currently contains seed/placeholder items | Project owner |
| Delivery | Confirm shipping regions, charges, processing times, and returns | Current promises are sample copy | Project owner |
| Containers | Enable this workspace to access the Docker daemon | The current session cannot connect to `/var/run/docker.sock`, so local container testing uses host runtime | Environment owner |

Move a resolved item to [decisions.md](decisions.md), then add the resulting work to [TODO.md](TODO.md).
