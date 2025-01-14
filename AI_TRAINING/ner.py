import spacy
import csv

class ner():


    nlp = spacy.load("en_core_web_md")


        # sample dataset 1
    texts = [
        "Alice went skiing in February in Colorado. She joined the ski club recently. Alice said, 'I went skiing down green slopes and stumbled a lot, but it was fun.'",
        "Maria ran a marathon in New York City last weekend. She trained for months, and the event was challenging but rewarding. Maria shared, 'I felt incredible crossing the finish line.'",
        "John went hiking in the Rocky Mountains in August. He reached the summit just in time for the sunset. John remarked, 'It was a breathtaking view from up there.'",
        "Sarah spent the day at the beach in California last Saturday. She built sandcastles and swam in the ocean. Sarah laughed, 'The water was perfect for swimming.'",
        "James participated in a chess tournament in London last month. He faced some tough opponents but managed to win first place. James smiled, 'It was a thrilling competition!'",
        "Emma visited Paris for the first time last summer. She toured the Eiffel Tower and explored the Louvre Museum. Emma exclaimed, 'The art and architecture were amazing!'",
        "David ran a 5K race in his hometown last Sunday. He trained for a month and felt accomplished crossing the finish line. David said, 'I can't wait for the next race!'",
        "Sophia went camping in the Appalachian Mountains last autumn. She set up a tent by a beautiful lake and cooked dinner over a campfire. Sophia enjoyed, 'The peace and quiet were just what I needed.'",
        "Liam attended a cooking class in Rome last spring. He learned to make traditional Italian pasta dishes. Liam said, 'I can’t wait to try these recipes at home!'",
        "Olivia participated in a yoga retreat in Bali last year. She practiced mindfulness and meditation every morning. Olivia shared, 'It was the most relaxing experience of my life.'"
        "Ethan visited Tokyo during the cherry blossom season. He explored the vibrant city and took part in a tea ceremony. Ethan said, 'The culture here is incredible!'",
        "Charlotte ran a half-marathon in Chicago in October. She trained for months and felt a great sense of achievement at the finish line. Charlotte said, 'I’m so proud of my progress!'",
        "Benjamin spent a week in the Swiss Alps last winter. He enjoyed skiing on the snowy slopes and relaxing by the fireplace. Benjamin remarked, 'The scenery was absolutely breathtaking!'",
        "Isabella went on a road trip along the Pacific Coast Highway last summer. She visited many beaches and enjoyed the sunsets. Isabella shared, 'This trip was everything I needed!'",
        "Henry went to a rock climbing gym for the first time last week. He climbed several walls and felt a rush of adrenaline. Henry said, 'I’m definitely going to do this again!'",
        "Mia attended a photography workshop in New Zealand last winter. She learned new techniques for capturing landscapes and portraits. Mia said, 'I can’t wait to apply what I’ve learned!'",
        "Lucas visited Barcelona last spring. He explored the city's architecture, including Gaudí’s famous Sagrada Família. Lucas said, 'The architecture here is out of this world!'",
        "Ava took a painting class in Florence during the summer. She learned to paint landscapes with watercolors. Ava said, 'It was amazing to capture the beauty of Italy on canvas!'",
        "Zoe went backpacking in the Canadian Rockies last year. She hiked along scenic trails and camped under the stars. Zoe shared, 'The views from the top were worth every step!'",
        "Jack participated in a football tournament in Madrid last summer. His team made it to the finals, and although they didn’t win, Jack said, 'It was an unforgettable experience!'",
        "Grace joined a sailing trip around the Greek Islands last spring. She spent the days on the water and the evenings in charming coastal towns. Grace said, 'It was the perfect getaway!'"
        
        
        "Emma visited Paris for the first time last summer. She toured the Eiffel Tower and explored the Louvre Museum. Emma exclaimed, 'The art and architecture were amazing!'",
        "Emma traveled to Rome during the spring holidays. She visited the Colosseum and enjoyed Italian cuisine. Emma said, 'The food here is incredible!'",
        "Last winter, Emma went on a backpacking trip to the Swiss Alps. She spent a few days hiking in the mountains and enjoying the snow. Emma remarked, 'The views were stunning!'",
        "Emma took a vacation to Tokyo in early spring. She visited the cherry blossom parks and attended a traditional tea ceremony. Emma commented, 'The culture here is so rich!'",
        "During the autumn, Emma spent a week in Barcelona. She explored the famous Sagrada Familia and walked through the Gothic Quarter. Emma said, 'Barcelona is full of history!'",
        "Emma went on a road trip along the Pacific Coast Highway last summer. She visited several beach towns and admired the ocean views. Emma shared, 'This was the best road trip ever!'",
        "In the fall, Emma went to New York City to attend a fashion event. She visited Central Park and explored various art galleries. Emma exclaimed, 'New York has so much to offer!'",
        "Emma visited London last year for a cultural exchange program. She toured Buckingham Palace and the Tower of London. Emma said, 'London is full of rich history!'",
        "Emma traveled to Kyoto in Japan last spring to experience traditional tea ceremonies and visit ancient temples. She shared, 'Kyoto feels like stepping back in time.'",
        "During her summer break, Emma went to Bali for a yoga retreat. She practiced meditation and enjoyed the peaceful beaches. Emma shared, 'Bali is truly a paradise.'"
    ]

    output_file = "AI_TRAINING/tokenized_data.csv"

    # Process texts
    data = []
    for i, text in enumerate(texts):
        doc = nlp(text)
        tokens = [token.text for token in doc]  # Tokenized words
        entities = [(ent.text, ent.label_) for ent in doc.ents]  # Named entities
        data.append({
            "Text ID": i + 1,
            "Original Text": text,
            "Tokens": ", ".join(tokens),
            "Entities": ", ".join([f"{ent[0]} ({ent[1]})" for ent in entities])
        })

    # Write to CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Text ID", "Original Text", "Tokens", "Entities"])
        writer.writeheader()
        writer.writerows(data)

    print(f"Tokenized data saved to {output_file}")
