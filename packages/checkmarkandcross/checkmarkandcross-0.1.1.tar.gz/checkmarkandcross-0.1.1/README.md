# Check Mark and Cross
```bash
python -m venv venv
source venv/bin/activate

pip install checkmarkandcross
```

```python
from checkmarkandcross import image

# check mark 512x512
image(True, 512)

# cross 16x16
image(False, 16)
```
