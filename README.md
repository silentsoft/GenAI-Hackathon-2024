# GenAI Hackathon 2024

![](/images/screenshot.png)

## Image Size Comparison

<table>
    <tr>
        <th></th>
        <th>Before (NAS/Storage)</th>
        <th>After (NAS/Storage)</th>
        <th>Reconstruct</th>
    </tr>
    <tr>
        <td>Files</td>
        <td>
            source_pcb_1.png (1.9MB)<br>
            source_pcb_2.png (2MB)<br>
            source_pcb_3.png (2MB)
        </td>
        <td>
            overlap_image1_1.avif (259KB)<br>
            non_overlap_image1_1.avif (323 bytes)<br>
            non_overlap_image1_2.avif (368 bytes)<br>
            non_overlap_image1_3.avif (370 bytes)<br>
            non_overlap_image2_3.avif (334 bytes)<br>
            non_overlap_image3_2.avif (342 bytes)
        </td>
        <td>
            reconstructed_image1.avif (258.KB)<br>
            reconstructed_image2.avif (258.KB)<br>
            reconstructed_image3.avif (258.KB)
        </td>
    </tr>
    <tr>
        <td>Total</td>
        <td>5.9MB</td>
        <td>261KB</td>
        <td>774KB</td>
    </tr>
</table>

## Installation

```shell
$ pip install -r requirements.txt
```

## Launch

```shell
$ cd hackathon
$ python3 main.py
```