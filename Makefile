doc:
	python doc.py -f $(FILE) --kernel-path $(KERNEL_PATH)
clean:
	rm --force /tmp/batch_find_*.cocci
	rm --force /tmp/out.batch_find_*.cocci
	rm --force description.txt
	rm --force sysfs_doc
