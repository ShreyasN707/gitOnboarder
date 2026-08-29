from app.repository_loader import (
    should_index,
    create_document,
    split_documents,
)


print(should_index("Simulator.cpp"))
print(should_index("node_modules/test.js"))
print(should_index("image.png"))


document = create_document(
    "Simulator.cpp",
    """
    void Simulator::recoverDeadlock() {

        // Find deadlocked processes

        // Terminate a process

        // Release its resources

        // Rebuild the wait-for graph
    }
    """
)


chunks = split_documents([document])

print("Number of chunks:", len(chunks))

for chunk in chunks:
    print("\n---")
    print(chunk.metadata)
    print(chunk.page_content)